# backend/conftest.py

import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy import JSON, Text
from sqlalchemy.ext.compiler import compiles

from app.main import app
from app.Infrastructure.db import Base
# Import all models to ensure they are registered with Base
from app.Models import auth_user, role, tag, trade, trades_tags, user_dashboard_layout, user_role

# This is a hack to make the tests work with SQLite
@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"

@compiles(ARRAY, "sqlite")
def compile_array_sqlite(type_, compiler, **kw):
    return "JSON"


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
    return create_async_engine(TEST_DATABASE_URL, echo=True)

@pytest.fixture(scope="session")
async def tables(engine):
    # Remove schema for sqlite
    for table in Base.metadata.tables.values():
        table.schema = None
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def db_session(engine, tables) -> AsyncGenerator[AsyncSession, None]:
    """Fixture for a db session."""
    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_factory() as session:
        yield session


@pytest.fixture(scope="function")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture for an async client to make requests to the app.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

# --- Fixtures for Sync Tests ---

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.Services.auth_service import get_current_user
from app.Models.auth_user import AuthUser
import uuid

SYNC_TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def sync_engine():
    # The echo=False is to avoid too much noise in the logs
    return create_engine(SYNC_TEST_DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)

@pytest.fixture(scope="session")
def sync_tables(sync_engine):
    # Remove schema for sqlite
    for table in Base.metadata.tables.values():
        table.schema = None
    Base.metadata.create_all(bind=sync_engine)
    yield
    Base.metadata.drop_all(bind=sync_engine)

@pytest.fixture(scope="function")
def db_session_sync(sync_engine, sync_tables):
    """Fixture for a sync db session."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture(scope="function")
def test_client_sync(db_session_sync):
    """
    Creates a sync test client, overriding dependencies.
    """
    def override_get_db():
        yield db_session_sync

    mock_user_id = uuid.uuid4()
    mock_user_email = "test@example.com"

    def override_get_current_user():
        # Check if user exists, if not create it
        user = db_session_sync.query(AuthUser).filter_by(id=mock_user_id).first()
        if not user:
            user = AuthUser(id=mock_user_id, email=mock_user_email)
            db_session_sync.add(user)
            db_session_sync.commit()
        return user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
