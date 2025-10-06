# backend/conftest.py

import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
import uuid

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy import JSON, select
from sqlalchemy.ext.compiler import compiles

from app.main import app
from app.Infrastructure.db import Base, get_db
from app.Router.auth import get_current_claims
# Import all models to ensure they are registered with Base
from app.Models import (
    auth_user, role, tag, trade, trades_tags, user_dashboard_layout, user_role,
    general_account, trading_account, broker, asset, asset_class, mistake,
    playbook, news_impact, psychology_state, trades_mistakes,
    trades_news_impacts, trades_psychology, request_log
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

@pytest.fixture(scope="session")
def test_session_maker(engine):
    """Factory for creating test database sessions."""
    return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
async def db_session(test_session_maker, tables) -> AsyncGenerator[AsyncSession, None]:
    """Fixture for an async db session."""
    async with test_session_maker() as session:
        yield session


@pytest.fixture(autouse=True)
def override_session_local(mocker, test_session_maker):
    """
    Patches SessionLocal where it's used by the middleware to ensure it uses
    the test database. This is crucial because middleware often does not use
    the standard dependency injection flow for database sessions.
    """
    mocker.patch("app.Middleware.request_logging.SessionLocal", new=test_session_maker)


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

@pytest.fixture
async def admin_role(db_session: AsyncSession) -> role.Role:
    """
    Ensures the 'admin' role exists and returns it. This fixture is crucial
    to ensure that the admin role is created and committed before any user
    that depends on it.
    """
    # Use a separate select to check for the role first.
    stmt = select(role.Role).where(role.Role.name == "admin")
    result = await db_session.execute(stmt)
    admin_role_obj = result.scalar_one_or_none()

    if not admin_role_obj:
        # If the role doesn't exist, create it and commit immediately.
        admin_role_obj = role.Role(name="admin", description="Administrator")
        db_session.add(admin_role_obj)
        await db_session.commit()
        await db_session.refresh(admin_role_obj)

    return admin_role_obj


# Helper to create a user and return their claims
async def create_test_user(db_session: AsyncSession, is_admin: bool, admin_role_obj: role.Role) -> dict:
    user_id = uuid.uuid4()
    user_type = 'admin' if is_admin else 'user'
    user_email = f"testuser_{user_type}_{uuid.uuid4()}@example.com"

    user = AuthUser(id=user_id, email=user_email, is_sso_user=False, is_anonymous=False)
    db_session.add(user)

    if is_admin:
        user_admin_role = user_role.UserRole(user_id=user_id, role_id=admin_role_obj.id)
        db_session.add(user_admin_role)

    await db_session.commit()
    return {"sub": str(user_id), "email": user_email}


@pytest.fixture
async def authenticated_client_factory(db_session: AsyncSession, admin_role: role.Role):
    @asynccontextmanager
    async def factory(is_admin: bool = False):
        claims = await create_test_user(db_session, is_admin, admin_role)

        async def override_get_db():
            yield db_session

        async def override_get_current_claims():
            return claims

        original_overrides = app.dependency_overrides.copy()
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_claims] = override_get_current_claims

        try:
            async with AsyncClient(app=app, base_url="http://test", follow_redirects=True) as client:
                yield client
        finally:
            app.dependency_overrides = original_overrides

    return factory