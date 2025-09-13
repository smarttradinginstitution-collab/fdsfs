# app/Infrastructure/db.py
from __future__ import annotations

import os
import ssl
import logging
from pathlib import Path
from typing import AsyncGenerator, Dict, Any
import traceback

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import declarative_base
from sqlalchemy import text

from app.config import settings

Base = declarative_base()
logger = logging.getLogger(__name__)

# Base dir del progetto "backend" (db.py è in backend/app/Infrastructure/db.py)
BACKEND_DIR = Path(__file__).resolve().parents[2]
CERTS_DIR = BACKEND_DIR / "certs"


def _resolve_path(p: str | None) -> Path | None:
    if not p:
        return None
    path = Path(p)
    return path if path.is_absolute() else (BACKEND_DIR / path)


def _combine_bundles(certifi_path: Path, extra_path: Path, out_path: Path) -> Path:
    """
    Crea un bundle combinato: bundle di certifi + certificato/i extra (PEM).
    Evita duplicati banali concatenando solo se il contenuto extra non è già presente.
    """
    data = certifi_path.read_bytes()
    extra = extra_path.read_bytes()
    if extra not in data:
        data += b"\n" + extra
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(data)
    return out_path


def _make_ssl_context() -> dict:
    """
    Per asyncpg serve connect_args={'ssl': <SSLContext|bool>}.

    Modalità (via env):
      - DB_SSL_VERIFY=false  -> disabilita verifica (solo test, MAI in prod)
      - DB_SSL_CA_MODE=certifi -> usa solo certifi
      - DB_SSL_CA_MODE=custom  -> usa solo SSL_CERT_FILE (percorso assoluto)
      - DB_SSL_CA_MODE=merge   -> certifi + SSL_CERT_FILE

    Logghiamo a stdout quali CA vengono caricati per debuggare facilmente.
    """
    from pathlib import Path

    if "+asyncpg" not in settings.DATABASE_URL:
        return {}

    # bypass (solo per test locali)
    if settings.ENV != "prod" and not settings.DB_SSL_VERIFY:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        print("[db] SSL: VERIFY DISABLED (solo dev)")
        return {"ssl": ctx}

    mode = (getattr(settings, "DB_SSL_CA_MODE", "certifi") or "certifi").lower()
    custom_path = getattr(settings, "SSL_CERT_FILE", "") or ""
    custom_abs = None

    # Risolvi percorso del PEM relativo al progetto (backend/certs/corp-root.pem)
    if custom_path:
        base_dir = Path(__file__).resolve().parent.parent  # .../backend/app
        # prova: se è relativo, riferisciti alla root del backend
        p = Path(custom_path)
        custom_abs = (base_dir.parent / p) if not p.is_absolute() else p
        custom_abs = custom_abs.resolve()

    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    # forza TLS 1.2+
    if hasattr(ssl, "TLSVersion"):
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.check_hostname = True
    ctx.verify_mode = ssl.CERT_REQUIRED

    loaded = []

    # carica certifi
    if mode in ("certifi", "merge"):
        try:
            import certifi  # type: ignore
            cafile = certifi.where()
            ctx.load_verify_locations(cafile=cafile)
            loaded.append(f"certifi={cafile}")
        except Exception as e:
            print(f"[db] SSL: ERRORE nel caricare certifi: {e!r}")

    # carica il tuo PEM
    if mode in ("custom", "merge") and custom_abs:
        if custom_abs.exists():
            try:
                ctx.load_verify_locations(cafile=str(custom_abs))
                loaded.append(f"custom={custom_abs}")
            except Exception as e:
                print(f"[db] SSL: ERRORE nel caricare custom CA '{custom_abs}': {e!r}")
        else:
            print(f"[db] SSL: custom CA NON TROVATO: {custom_abs}")

    if not loaded:
        # fallback di sicurezza: almeno il trust store di sistema
        print("[db] SSL: nessun CA esplicito caricato, fallback store di sistema")
        ctx = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)

    print(f"[db] SSL: verify=ON, mode={mode}, loaded=({', '.join(loaded)})")
    return {"ssl": ctx}


# Engine: con pool pre-ping e NullPool (compatibile con pooler esterni tipo pgBouncer/Supabase)
engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=False,
    pool_pre_ping=True,
    connect_args=_make_ssl_context(),
    poolclass=NullPool,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        # Normalizza il fuso orario a UTC per coerenza lato DB
        await session.execute(text("SET TIME ZONE 'UTC'"))
        yield session


# Utility opzionali

async def check_connection() -> bool:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        # LOG verboso: mostra tipo, messaggio e stack
        print("[db:check_connection] ERROR:", repr(e))
        traceback.print_exc()
        return False

async def dispose_engine() -> None:
    await engine.dispose()
