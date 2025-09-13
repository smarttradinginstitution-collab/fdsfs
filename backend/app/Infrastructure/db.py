# app/Infrastructure/db.py
from __future__ import annotations

import ssl
import traceback
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from app.config import settings

Base = declarative_base()


def _make_ssl_context() -> dict:
    """
    Costruisce il contesto SSL per asyncpg.
    Modalità supportate (DB_SSL_CA_MODE):
      - system         -> trust store di sistema (Windows/OS)
      - certifi        -> solo bundle certifi
      - custom         -> solo PEM indicato da SSL_CERT_FILE
      - merge          -> certifi + custom
      - system+custom  -> sistema + custom (utile in reti aziendali)

    Nota: usiamo sempre SSLContext(PROTOCOL_TLS_CLIENT) e abilitiamo TLS1.2+.
    """
    if "+asyncpg" not in settings.DATABASE_URL:
        return {}

    # Dev bypass solo se non-prod e DB_SSL_VERIFY=false
    if settings.ENV != "prod" and not settings.DB_SSL_VERIFY:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        print("[db] SSL: VERIFY DISABLED (dev)")
        return {"ssl": ctx}

    mode = settings.DB_SSL_CA_MODE
    custom_path = settings.resolve_path(settings.SSL_CERT_FILE) if settings.SSL_CERT_FILE else None

    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    if hasattr(ssl, "TLSVersion"):
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.check_hostname = True
    ctx.verify_mode = ssl.CERT_REQUIRED

    loaded = []

    def load_system():
        # Store nativo (Windows/Mac/Linux)
        ctx.load_default_certs(purpose=ssl.Purpose.SERVER_AUTH)
        loaded.append("system")

    def load_certifi():
        import certifi  # type: ignore
        ctx.load_verify_locations(cafile=certifi.where())
        loaded.append(f"certifi={certifi.where()}")

    def load_custom(p: Path):
        if not p.exists():
            print(f"[db] SSL: custom CA NON TROVATO: {p}")
            return
        ctx.load_verify_locations(cafile=str(p))
        loaded.append(f"custom={p}")

    if mode == "system":
        load_system()
    elif mode == "certifi":
        load_certifi()
    elif mode == "custom":
        if custom_path:
            load_custom(custom_path)
        else:
            print("[db] SSL: custom selezionato, ma SSL_CERT_FILE non impostato")
    elif mode == "merge":
        # storicamente: certifi + custom
        load_certifi()
        if custom_path:
            load_custom(custom_path)
    elif mode == "system+custom":
        load_system()
        if custom_path:
            load_custom(custom_path)

    if not loaded:
        # Fallback sicuro
        ctx = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
        print("[db] SSL: fallback a create_default_context() (nessun CA esplicito caricato)")

    print(f"[db] SSL: verify=ON, mode={mode}, loaded=({', '.join(loaded)})")
    return {"ssl": ctx}


engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=False,
    pool_pre_ping=True,
    connect_args=_make_ssl_context(),
    poolclass=NullPool,
)

SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        await session.execute(text("SET TIME ZONE 'UTC'"))
        yield session


async def check_connection() -> bool:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print("[db:check_connection] ERROR:", repr(e))
        traceback.print_exc()
        return False


async def dispose_engine() -> None:
    await engine.dispose()
