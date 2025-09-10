# backend/tests/conftest.py
#
# File di configurazione per Pytest. Contiene le "fixture", ovvero funzioni
# di setup che preparano l'ambiente per i nostri test di integrazione.
#
# STRATEGIA DI TEST:
# 1. DATABASE: Usiamo un database SQLite in-memoria, veloce e isolato.
#    Le tabelle vengono create e distrutte per ogni test.
# 2. APPLICAZIONE: Usiamo l'istanza reale dell'app FastAPI.
# 3. DIPENDENZE: Sovrascriviamo (`override`) due dipendenze chiave:
#    - `get_db`: per puntare al nostro database di test.
#    - `get_current_claims`: per simulare l'autenticazione di utenti specifici.
# 4. CLIENT: Usiamo `AsyncClient` di HTTPX per inviare richieste reali all'app.

import asyncio
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import JSON
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.Infrastructure.db import Base, get_db
from app.Router.auth import get_current_claims
from app.Models.trade import Trade, TradeDirectionEnum
from app.Models.auth_user import AuthUser


# === RICETTA DI COMPILAZIONE PER JSONB -> JSON (per SQLite) ===
# Aggiungiamo una "ricetta" di compilazione per il tipo JSONB
# quando il dialetto è 'sqlite'.
# Questo dice a SQLAlchemy: "Quando provi a creare una colonna JSONB
# su SQLite, usa invece il tipo generico JSON".
@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return compiler.visit_JSON(type_, **kw)


# === RICETTA DI COMPILAZIONE PER ARRAY -> JSON (per SQLite) ===
# Stesso approccio del JSONB, ma per il tipo ARRAY di Postgres.
# Lo trattiamo come un campo JSON generico in SQLite.
@compiles(ARRAY, "sqlite")
def compile_array_sqlite(type_, compiler, **kw):
    return compiler.visit_JSON(type_, **kw)


# URL per il database di test SQLite in-memoria
# `StaticPool` è raccomandato per SQLite in-memoria con SQLAlchemy async
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Necessario per SQLite
    poolclass=StaticPool,
)
TestSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture che fornisce una sessione di database di test per ogni test.
    Crea tutte le tabelle prima del test e le elimina dopo.
    """
    # === MODIFICA per compatibilità SQLite (Jules, 10/09/2025) ===
    # Rimuoviamo lo schema 'public' da tutti i modelli prima di creare le tabelle.
    # Questo è necessario perché SQLite non supporta gli schemi di PostgreSQL.
    for table in Base.metadata.sorted_tables:
        table.schema = None

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function", autouse=True)
def override_get_db(db_session: AsyncSession):
    """
    Sovrascrive la dipendenza `get_db` dell'app per usare la sessione
    del database di test. `autouse=True` la applica a tutti i test.
    """
    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    yield
    # Ripristina le dipendenze originali dopo il test
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Fornisce un client HTTP asincrono per i test."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# --- Fixture per Utenti e Autenticazione ---

@pytest.fixture(scope="function")
def user_a_uuid() -> uuid4:
    return uuid4()


@pytest.fixture(scope="function")
def user_b_uuid() -> uuid4:
    return uuid4()


def mock_authentication(user_uuid: uuid4):
    """Factory per sovrascrivere l'autenticazione con i claims dati."""
    claims = {"sub": str(user_uuid)}
    app.dependency_overrides[get_current_claims] = lambda: claims


@pytest_asyncio.fixture
async def user_a(db_session: AsyncSession, user_a_uuid: uuid4) -> AuthUser:
    """Crea l'utente A nel database di test."""
    user = AuthUser(id=user_a_uuid, email="user.a@test.com")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def user_b(db_session: AsyncSession, user_b_uuid: uuid4) -> AuthUser:
    """Crea l'utente B nel database di test."""
    user = AuthUser(id=user_b_uuid, email="user.b@test.com")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# --- Fixture per Dati di Test ---

@pytest_asyncio.fixture
async def trade_for_user_a(db_session: AsyncSession, user_a: AuthUser) -> Trade:
    """Crea un trade per l'utente A nel database di test."""
    trade = Trade(
        id=uuid4(),
        user_id=user_a.id,
        symbol="TESTA",
        p_l=100.0,
        direction=TradeDirectionEnum.Long,
    )
    db_session.add(trade)
    await db_session.commit()
    await db_session.refresh(trade)
    return trade
