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
from app.Models.trading_account import TradingAccount
from app.Models.general_account import GeneralAccount
from app.Router.auth import get_current_claims

# ------------------------------
# Fixtures
# ------------------------------

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

# ------------------------------
# Tests
# ------------------------------

@pytest.mark.anyio
async def test_create_broker_as_admin(admin_client: AsyncClient):
    """Admin can create a new broker."""
    response = await admin_client.post("/api/v1/brokers/", json={"name": "New Broker"})
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "New Broker"
    assert "id" in data

@pytest.mark.anyio
async def test_create_broker_as_user(user_client: AsyncClient):
    """Regular user cannot create a broker."""
    response = await user_client.post("/api/v1/brokers/", json={"name": "Forbidden Broker"})
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.anyio
async def test_create_broker_duplicate_name(admin_client: AsyncClient, test_broker: Broker):
    """Cannot create a broker with a duplicate name."""
    response = await admin_client.post("/api/v1/brokers/", json={"name": test_broker.name})
    assert response.status_code == status.HTTP_409_CONFLICT

@pytest.mark.anyio
async def test_get_all_brokers(user_client: AsyncClient, test_broker: Broker):
    """Any authenticated user can list all brokers."""
    response = await user_client.get("/api/v1/brokers/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(b["id"] == str(test_broker.id) for b in data)

@pytest.mark.anyio
async def test_get_broker_by_id(user_client: AsyncClient, test_broker: Broker):
    """Any authenticated user can get a broker by ID."""
    response = await user_client.get(f"/api/v1/brokers/{test_broker.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(test_broker.id)
    assert data["name"] == test_broker.name

@pytest.mark.anyio
async def test_get_broker_not_found(user_client: AsyncClient):
    """Getting a non-existent broker returns 404."""
    non_existent_id = uuid4()
    response = await user_client.get(f"/api/v1/brokers/{non_existent_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.anyio
async def test_update_broker_as_admin(admin_client: AsyncClient, test_broker: Broker):
    """Admin can update a broker."""
    new_name = "Updated Broker Name"
    response = await admin_client.put(f"/api/v1/brokers/{test_broker.id}", json={"name": new_name})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == new_name

@pytest.mark.anyio
async def test_update_broker_as_user(user_client: AsyncClient, test_broker: Broker):
    """Regular user cannot update a broker."""
    response = await user_client.put(f"/api/v1/brokers/{test_broker.id}", json={"name": "Forbidden Name"})
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.anyio
async def test_delete_broker_as_admin(admin_client: AsyncClient, db_session: AsyncSession):
    """Admin can delete a broker if it has no dependencies."""
    broker_to_delete = Broker(name=f"Deletable Broker {uuid4()}")
    db_session.add(broker_to_delete)
    await db_session.commit()

    response = await admin_client.delete(f"/api/v1/brokers/{broker_to_delete.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify it's gone
    deleted = await db_session.get(Broker, broker_to_delete.id)
    assert deleted is None

@pytest.mark.anyio
async def test_delete_broker_as_user(user_client: AsyncClient, test_broker: Broker):
    """Regular user cannot delete a broker."""
    response = await user_client.delete(f"/api/v1/brokers/{test_broker.id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.anyio
async def test_delete_broker_with_dependencies(admin_client: AsyncClient, test_broker: Broker, db_session: AsyncSession, regular_user: AuthUser):
    """Cannot delete a broker if it's linked to a trading account."""
    # Create a GeneralAccount first, as TradingAccount depends on it
    general_account = GeneralAccount(user_id=regular_user.id, label="Test General Account")
    db_session.add(general_account)
    await db_session.flush()

    # Now, create the TradingAccount which acts as a dependency
    trading_account = TradingAccount(
        label="My Dependent Trading Account",
        broker_id=test_broker.id,
        general_account_id=general_account.id
    )
    db_session.add(trading_account)
    await db_session.commit()

    response = await admin_client.delete(f"/api/v1/brokers/{test_broker.id}")
    assert response.status_code == status.HTTP_409_CONFLICT
    assert "associated with other resources" in response.json()["detail"]