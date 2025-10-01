import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from fastapi import status

from app.main import app
from sqlalchemy import select
from app.Models.asset import Asset
from app.Models.asset_class import AssetClass
from app.Models.role import Role
from app.Models.auth_user import AuthUser
from app.Models.user_role import UserRole
from app.Router.auth import get_current_claims

# Re-using fixtures from the previous test file for consistency

@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio", {"use_uvloop": True}

@pytest.fixture
async def admin_user(db_session: AsyncSession) -> AuthUser:
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
    asset_class = AssetClass(name=f"Dependency Class {uuid4()}")
    db_session.add(asset_class)
    await db_session.commit()
    return asset_class

@pytest.fixture
async def test_asset(db_session: AsyncSession, test_asset_class: AssetClass) -> Asset:
    asset = Asset(
        symbol="TEST",
        name="Test Asset",
        asset_class_id=test_asset_class.id
    )
    db_session.add(asset)
    await db_session.commit()
    return asset

# Tests for Assets

@pytest.mark.anyio
async def test_create_asset_as_admin(admin_client: AsyncClient, test_asset_class: AssetClass):
    payload = {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "asset_class_id": str(test_asset_class.id),
        "market": "NASDAQ"
    }
    response = await admin_client.post("/api/v1/assets/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert data["name"] == "Apple Inc."

@pytest.mark.anyio
async def test_create_asset_as_user(user_client: AsyncClient, test_asset_class: AssetClass):
    payload = {"symbol": "GOOG", "name": "Google LLC", "asset_class_id": str(test_asset_class.id)}
    response = await user_client.post("/api/v1/assets/", json=payload)
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.anyio
async def test_create_asset_symbol_too_long(admin_client: AsyncClient, test_asset_class: AssetClass):
    payload = {"symbol": "THISISWAYTOOLONG", "name": "Long Symbol", "asset_class_id": str(test_asset_class.id)}
    response = await admin_client.post("/api/v1/assets/", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.anyio
async def test_create_asset_nonexistent_class(admin_client: AsyncClient):
    payload = {"symbol": "NOCLASS", "name": "No Class", "asset_class_id": str(uuid4())}
    response = await admin_client.post("/api/v1/assets/", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.anyio
async def test_get_all_assets(user_client: AsyncClient, test_asset: Asset):
    response = await user_client.get("/api/v1/assets/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert any(a["id"] == str(test_asset.id) for a in data)

@pytest.mark.anyio
async def test_get_asset_by_id(user_client: AsyncClient, test_asset: Asset):
    response = await user_client.get(f"/api/v1/assets/{test_asset.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(test_asset.id)

@pytest.mark.anyio
async def test_update_asset_as_admin(admin_client: AsyncClient, test_asset: Asset):
    response = await admin_client.put(f"/api/v1/assets/{test_asset.id}", json={"name": "Updated Asset Name"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Asset Name"

@pytest.mark.anyio
async def test_update_asset_as_user(user_client: AsyncClient, test_asset: Asset):
    response = await user_client.put(f"/api/v1/assets/{test_asset.id}", json={"name": "Forbidden Update"})
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.anyio
async def test_delete_asset_as_admin(admin_client: AsyncClient, db_session: AsyncSession, test_asset_class: AssetClass):
    asset_to_delete = Asset(symbol="DEL", name="ToDelete", asset_class_id=test_asset_class.id)
    db_session.add(asset_to_delete)
    await db_session.commit()

    response = await admin_client.delete(f"/api/v1/assets/{asset_to_delete.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    deleted = await db_session.get(Asset, asset_to_delete.id)
    assert deleted is None

@pytest.mark.anyio
async def test_delete_asset_as_user(user_client: AsyncClient, test_asset: Asset):
    response = await user_client.delete(f"/api/v1/assets/{test_asset.id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN