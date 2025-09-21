# backend/conftest.py

from dotenv import load_dotenv
import os
import pytest
import asyncio
from typing import AsyncGenerator

# Load environment variables from .env file for testing.
# This must be done before the app and its settings are imported.
print("Loading .env file for tests...")
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    print(f"Found .env file at: {dotenv_path}")
    load_dotenv(dotenv_path=dotenv_path)
else:
    print("No .env file found, setting dummy environment variables.")
    # If no .env file, set dummy values to satisfy settings validation during tests
    os.environ.setdefault('SNAPTRADE_CLIENT_ID', 'dummy_client_id')
    os.environ.setdefault('SNAPTRADE_CONSUMER_KEY', 'dummy_consumer_key')
    os.environ.setdefault('SUPABASE_PROJECT_URL', 'http://dummy.url')
    os.environ.setdefault('SUPABASE_KEY', 'dummy_key')
from httpx import AsyncClient

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy import JSON, Text
from sqlalchemy.ext.compiler import compiles

from app.main import app
from app.Infrastructure.db import Base
# Import all models to ensure they are registered with Base
# Import all models to ensure they are registered with Base.
# Ordering might matter for SQLAlchemy's metadata registration.
from app.Models import (
    profile,
    auth_user,
    role,
    brokerage_connection,
    security,
    brokerage_account,
    tag,
    trade,
    trades_tags,
    user_dashboard_layout,
    user_role,
    option_symbol,
    account_balance,
    account_position,
    account_order,
    account_activity
)

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
