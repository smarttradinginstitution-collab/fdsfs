# backend/conftest.py

import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
import uuid

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy import JSON
from sqlalchemy.ext.compiler import compiles

from app.main import app
from app.Infrastructure.db import Base, get_db
from app.Router.auth import get_current_claims
# Import all models to ensure they are registered with Base
from app.Models import (
    auth_user, role, tag, trade, trades_tags, user_dashboard_layout, user_role,
    general_account, trading_account, broker, asset, asset_class, mistake,
    playbook, news_impact, psychology_state, trades_mistakes, trades_playbooks,
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
def event_loop():
    """Create an instance of the default event loop for each test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

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
async def db_session(engine, tables) -> AsyncGenerator[AsyncSession, None]:
    """Fixture for an async db session."""
    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_factory() as session:
        yield session

@pytest.fixture
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture for an async client, overriding db and auth dependencies.
    """
    mock_user_id = uuid.uuid4()
    mock_user_email = "test@example.com"

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    async def override_get_current_claims() -> dict:
        user = await db_session.get(AuthUser, mock_user_id)
        if not user:
            user = AuthUser(
                id=mock_user_id,
                email=mock_user_email,
                is_sso_user=False,
                is_anonymous=False,
            )
            db_session.add(user)
            await db_session.commit()
        return {"sub": str(mock_user_id), "email": mock_user_email}

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_claims] = override_get_current_claims

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()