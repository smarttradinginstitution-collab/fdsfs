import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import uuid4
from fastapi import status

from app.main import app
from app.Models.broker import Broker
from app.Models.role import Role
from app.Models.auth_user import AuthUser
from app.Models.user_role import UserRole
from app.Router.auth import get_current_claims

@pytest.fixture(scope="module")
def anyio_backend():
    """Use asyncio for all tests in this module."""
    return "asyncio"

@pytest.fixture
async def admin_user(db_session: AsyncSession) -> AuthUser:
    """Creates an admin user, ensuring the 'admin' role exists."""
    stmt = select(Role).where(Role.name == "admin")
    result = await db_session.execute(stmt)
    admin_role = result.scalars().first()
    if not admin_role:
        admin_role = Role(id=uuid4(), name="admin", description="Administrator")
        db_session.add(admin_role)
        await db_session.flush()

    user = AuthUser(id=uuid4(), email=f"admin_{uuid4()}@test.com")
    db_session.add(user)
    await db_session.flush()

    user_role = UserRole(user_id=user.id, role_id=admin_role.id)
    db_session.add(user_role)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
async def regular_user(db_session: AsyncSession) -> AuthUser:
    """Creates a regular user for testing."""
    user = AuthUser(id=uuid4(), email=f"user_{uuid4()}@test.com")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
def admin_client(async_client: AsyncClient, admin_user: AuthUser) -> AsyncClient:
    """Provides a test client authenticated as an admin user."""
    app.dependency_overrides[get_current_claims] = lambda: {
        "sub": str(admin_user.id),
        "email": admin_user.email,
    }
    return async_client

@pytest.fixture
def user_client(async_client: AsyncClient, regular_user: AuthUser) -> AsyncClient:
    """Provides a test client authenticated as a regular user."""
    app.dependency_overrides[get_current_claims] = lambda: {
        "sub": str(regular_user.id),
        "email": regular_user.email,
    }
    return async_client

@pytest.fixture
async def test_broker(db_session: AsyncSession) -> Broker:
    """Fixture for a pre-existing broker."""
    broker = Broker(name=f"Test Broker Inc. {uuid4()}")
    db_session.add(broker)
    await db_session.commit()
    await db_session.refresh(broker)
    return broker