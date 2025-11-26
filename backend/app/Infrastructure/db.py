# app/Infrastructure/db.py
from __future__ import annotations

from typing import AsyncGenerator
import ssl
import sys

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

# Import all models here to ensure they are registered with SQLAlchemy's Base
# before any operation that needs them is executed. This prevents circular
# dependency errors between models with relationships.
from app.Models.asset import Asset
from app.Models.asset_class import AssetClass
from app.Models.auth_user import AuthUser
from app.Models.broker import Broker
from app.Models.broker_asset_class import BrokerAssetClass
from app.Models.general_account import GeneralAccount
from app.Models.mistake import Mistake
from app.Models.news_impact import NewsImpact
from app.Models.playbook import Playbook
from app.Models.psychology_state import PsychologyState
from app.Models.role import Role
from app.Models.tag import Tag
from app.Models.trade import Trade
from app.Models.trading_account import TradingAccount
from app.Models.trades_mistakes import TradesMistakes
from app.Models.trades_news_impacts import TradesNewsImpacts
from app.Models.trades_psychology import TradesPsychology
from app.Models.trades_tags import TradesTags
from app.Models.user_dashboard_layout import UserDashboardLayout
from app.Models.user_role import UserRole


def _make_ssl_context() -> dict:
    """
    Per asyncpg serve 'ssl': <SSLContext|bool>.
    - Se l'URL è asyncpg, costruiamo un SSLContext che usa il bundle CA di 'certifi'
      (evita errori su Windows dove il trust store può essere incompleto).
    - Se DB_SSL_VERIFY=false, usiamo un contesto che NON verifica (solo dev).
    """
    if "+asyncpg" not in settings.DATABASE_URL:
        return {}

    # bypass (solo dev)
    if settings.ENV != "prod" and not settings.DB_SSL_VERIFY:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return {"ssl": ctx}

    # verifica stretta con certifi
    try:
        import certifi  # type: ignore
        cafile = certifi.where()
        ctx = ssl.create_default_context(cafile=cafile)
        # opzionale: forza TLS 1.2+
        if hasattr(ssl, "PROTOCOL_TLS_CLIENT"):
            ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        return {"ssl": ctx}
    except Exception:
        # fallback: ssl=True (usa store di sistema)
        return {"ssl": True}


# In ambienti con un pooler esterno come pgBouncer (comune in Supabase),
# è raccomandato disabilitare il pooling di SQLAlchemy per evitare conflitti.
# NullPool crea e distrugge le connessioni per ogni operazione.
engine = create_async_engine(
    settings.DATABASE_URL,
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
        # Forza il fuso orario della sessione a UTC.
        # Questo garantisce che i timestamp "naive" inviati da Python (che non hanno fuso orario)
        # vengano interpretati come UTC quando inseriti in una colonna TIMESTAMPTZ,
        # e che le funzioni del database operino in modo coerente.
        await session.execute(text("SET TIME ZONE 'UTC'"))
        yield session


# Utilità opzionali

async def check_connection() -> bool:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


async def dispose_engine() -> None:
    await engine.dispose()
