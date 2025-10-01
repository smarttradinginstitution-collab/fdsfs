import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from fastapi import status

from app.main import app
from sqlalchemy import select
from app.Models.asset_class import AssetClass
from app.Models.role import Role
from app.Models.auth_user import AuthUser
from app.Models.user_role import UserRole
from app.Router.auth import get_current_claims

# Fixtures from conftest.py or a shared fixtures file would be ideal,
# but for simplicity, I'll define them here.

@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio", {"use_uvloop": True}

@pytest.fixture
async def admin_user(db_session: AsyncSession) -> AuthUser:
    """Creates an admin user, ensuring the 'admin' role exists."""
    result = await db_session.execute(select(Role).where(Role.name == "admin"))
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
    return user

@pytest.fixture
async def regular_user(db_session: AsyncSession) -> AuthUser:
    user = AuthUser(id=uuid4(), email=f"user_{uuid4()}@test.com")
    db_session.add(user)
    await db_session.commit()
    return user

@pytest.fixture
def admin_client(async_client: AsyncClient, admin_user: AuthUser) -> AsyncClient:
    app.dependency_overrides[get_current_claims] = lambda: {"sub": str(admin_user.id)}
    return async_client

@pytest.fixture
def user_client(async_client: AsyncClient, regular_user: AuthUser) -> AsyncClient:
    app.dependency_overrides[get_current_claims] = lambda: {"sub": str(regular_user.id)}
    return async_client

@pytest.fixture
async def test_asset_class(db_session: AsyncSession) -> AssetClass:
    asset_class = AssetClass(name=f"Test Class {uuid4()}")
    db_session.add(asset_class)
    await db_session.commit()
    return asset_class

# Tests for Asset Classes

@pytest.mark.anyio
async def test_create_asset_class_as_admin(admin_client: AsyncClient):
    response = await admin_client.post("/api/v1/asset-classes/", json={"name": "Stocks"})
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Stocks"

@pytest.mark.anyio
async def test_create_asset_class_as_user(user_client: AsyncClient):
    response = await user_client.post("/api/v1/asset-classes/", json={"name": "Bonds"})
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.anyio
async def test_create_asset_class_duplicate_name(admin_client: AsyncClient, test_asset_class: AssetClass):
    response = await admin_client.post("/api/v1/asset-classes/", json={"name": test_asset_class.name})
    assert response.status_code == status.HTTP_409_CONFLICT

@pytest.mark.anyio
async def test_get_all_asset_classes(user_client: AsyncClient, test_asset_class: AssetClass):
    response = await user_client.get("/api/v1/asset-classes/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert any(ac["id"] == str(test_asset_class.id) for ac in data)

@pytest.mark.anyio
async def test_get_asset_class_by_id(user_client: AsyncClient, test_asset_class: AssetClass):
    response = await user_client.get(f"/api/v1/asset-classes/{test_asset_class.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(test_asset_class.id)

@pytest.mark.anyio
async def test_update_asset_class_as_admin(admin_client: AsyncClient, test_asset_class: AssetClass):
    new_name = "Updated Class"
    response = await admin_client.put(f"/api/v1/asset-classes/{test_asset_class.id}", json={"name": new_name})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == new_name

@pytest.mark.anyio
async def test_update_asset_class_as_user(user_client: AsyncClient, test_asset_class: AssetClass):
    response = await user_client.put(f"/api/v1/asset-classes/{test_asset_class.id}", json={"name": "Forbidden Update"})
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.anyio
async def test_delete_asset_class_as_admin(admin_client: AsyncClient, db_session: AsyncSession):
    asset_class_to_delete = AssetClass(name="ToDelete")
    db_session.add(asset_class_to_delete)
    await db_session.commit()

    response = await admin_client.delete(f"/api/v1/asset-classes/{asset_class_to_delete.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify it's gone
    deleted = await db_session.get(AssetClass, asset_class_to_delete.id)
    assert deleted is None

@pytest.mark.anyio
async def test_delete_asset_class_as_user(user_client: AsyncClient, test_asset_class: AssetClass):
    response = await user_client.delete(f"/api/v1/asset-classes/{test_asset_class.id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN