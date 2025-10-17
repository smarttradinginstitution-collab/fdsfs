# backend/conftest.py
from dotenv import load_dotenv
import os

# Carica le variabili d'ambiente dal file .env del backend
# Assicurati che il percorso sia corretto rispetto a dove esegui pytest
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
else:
    # Se il file .env non esiste, imposta delle variabili d'ambiente fittizie
    # per permettere l'importazione dell'app senza errori.
    os.environ.setdefault("SUPABASE_URL", "http://localhost:54321")
    os.environ.setdefault("SUPABASE_ANON_KEY", "your-anon-key")
    os.environ.setdefault("SUPABASE_SERVICE_KEY", "your-service-key")


import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
import uuid

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy import JSON, select, event
from sqlalchemy.ext.compiler import compiles

from app.main import app
from app.Infrastructure.db import Base, get_db
from app.Router.auth import get_current_claims
# Import all models to ensure they are registered with Base
from app.Models import (
    auth_user, role, tag, trade, trades_tags, user_dashboard_layout, user_role,
    general_account, trading_account, broker, asset, asset_class, mistake,
    playbook, news_impact, psychology_state, trades_mistakes,
    trades_news_impacts, trades_psychology
)
from app.Models.auth_user import AuthUser

# This is a hack to make the tests work with SQLite
@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"

@compiles(ARRAY, "sqlite")
def compile_array_sqlite(type_, compiler, **kw):
    return "JSON"

from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy import Text

@compiles(CITEXT, "sqlite")
def compile_citext_sqlite(element, compiler, **kw):
    """
    Renders CITEXT as TEXT COLLATE NOCASE for SQLite, which provides
    case-insensitive text comparison.
    """
    return "TEXT COLLATE NOCASE"


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
async def engine():
    return create_async_engine(TEST_DATABASE_URL, echo=False)

@pytest.fixture(scope="session")
async def tables(engine):
    for table in Base.metadata.tables.values():
        table.schema = None
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def connection(engine, tables) -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture to create a connection with a transaction that is rolled back after each test.
    """
    async with engine.connect() as conn:
        trans = await conn.begin()
        yield conn
        await trans.rollback()


@pytest.fixture
async def db_session(connection) -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture that establishes a transaction, creates a savepoint, and rolls back
    to that savepoint after each test. This allows repositories to use commit()
    while maintaining test isolation.
    """
    # start a SAVEPOINT transaction
    nested = await connection.begin_nested()

    # if the SAVEPOINT transaction is ended, start a new one
    @event.listens_for(connection.sync_connection, "commit")
    def recommit(conn):
        if conn.get_nested_transaction():
            return

        if conn.get_transaction():
            conn.begin_nested()

    # bind an individual session to the connection
    session = AsyncSession(bind=connection, expire_on_commit=False)

    yield session

    # close the session
    await session.close()


# Fixture for a regular authenticated user client
@pytest.fixture
async def async_client(authenticated_client_factory):
    async with authenticated_client_factory(is_admin=False) as client:
        yield client

# Fixture for another regular authenticated user client
@pytest.fixture
async def other_user_async_client(authenticated_client_factory):
    async with authenticated_client_factory(is_admin=False) as client:
        yield client

# Fixture for an admin authenticated user client
@pytest.fixture
async def admin_async_client(authenticated_client_factory):
    async with authenticated_client_factory(is_admin=True) as client:
        yield client


from contextlib import asynccontextmanager

# Helper to create a user and return their claims
async def create_test_user(db_session: AsyncSession, is_admin: bool) -> dict:
    user_id = uuid.uuid4()
    user_type = 'admin' if is_admin else 'user'
    user_email = f"testuser_{user_type}_{uuid.uuid4()}@example.com"

    user = AuthUser(id=user_id, email=user_email, is_sso_user=False, is_anonymous=False)
    db_session.add(user)

    if is_admin:
        admin_role_result = await db_session.execute(select(role.Role).filter_by(name="admin"))
        admin_role = admin_role_result.scalar_one_or_none()
        if not admin_role:
            admin_role = role.Role(name="admin", description="Administrator")
            db_session.add(admin_role)
            await db_session.flush()
        user_admin_role = user_role.UserRole(user_id=user_id, role_id=admin_role.id)
        db_session.add(user_admin_role)

    await db_session.commit()
    return {"sub": str(user_id), "email": user_email}

@pytest.fixture
async def authenticated_client_factory(db_session: AsyncSession):
    @asynccontextmanager
    async def factory(is_admin: bool = False):
        claims = await create_test_user(db_session, is_admin)

        async def override_get_db():
            yield db_session

        async def override_get_current_claims():
            return claims

        original_overrides = app.dependency_overrides.copy()
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_claims] = override_get_current_claims

        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as client:
                yield client
        finally:
            app.dependency_overrides = original_overrides

    return factory