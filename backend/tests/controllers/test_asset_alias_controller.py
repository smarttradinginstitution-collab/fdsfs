import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from fastapi import status

from app.main import app
from sqlalchemy import select
from app.Models.asset import Asset
from app.Models.asset_class import AssetClass
from app.Models.asset_alias import AssetAlias
from app.Models.broker import Broker
from app.Models.platform import Platform
from app.Models.role import Role
from app.Models.auth_user import AuthUser
from app.Models.user_role import UserRole
from app.Router.auth import get_current_claims

# Fixtures
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

from app.Models.asset_market import AssetMarket

@pytest.fixture
async def test_asset_market(db_session: AsyncSession) -> AssetMarket:
    """Fixture for a pre-existing asset market."""
    asset_market = AssetMarket(name=f"Test Market {uuid4()}", code=f"TM{str(uuid4())[:4]}")
    db_session.add(asset_market)
    await db_session.commit()
    return asset_market

@pytest.fixture
async def test_asset_class(db_session: AsyncSession) -> AssetClass:
    """Fixture for a pre-existing asset class."""
    asset_class = AssetClass(name=f"Test Class {uuid4()}")
    db_session.add(asset_class)
    await db_session.commit()
    return asset_class

@pytest.fixture
async def test_asset(db_session: AsyncSession, test_asset_class: AssetClass, test_asset_market: AssetMarket) -> Asset:
    asset = Asset(
        symbol="ALIAS",
        name="Alias Asset",
        asset_class_id=test_asset_class.id,
        asset_market_id=test_asset_market.id
    )
    db_session.add(asset)
    await db_session.commit()
    return asset

@pytest.fixture
async def test_broker(db_session: AsyncSession) -> Broker:
    broker = Broker(name=f"Alias Broker {uuid4()}")
    db_session.add(broker)
    await db_session.commit()
    return broker

@pytest.fixture
async def test_platform(db_session: AsyncSession) -> Platform:
    platform = Platform(name=f"Alias Platform {uuid4()}")
    db_session.add(platform)
    await db_session.commit()
    return platform

@pytest.fixture
async def test_asset_alias(db_session: AsyncSession, test_asset: Asset) -> AssetAlias:
    alias = AssetAlias(asset_id=test_asset.id, alias="Primary Alias")
    db_session.add(alias)
    await db_session.commit()
    return alias

# Tests for Asset Aliases

@pytest.mark.anyio
async def test_create_alias_as_admin(admin_client: AsyncClient, test_asset: Asset, test_broker: Broker, test_platform: Platform):
    payload = {
        "asset_id": str(test_asset.id),
        "alias": "New.Alias",
        "broker_id": str(test_broker.id),
        "platform_id": str(test_platform.id),
        "is_primary": True,
    }
    response = await admin_client.post("/api/v1/asset-aliases/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["alias"] == "New.Alias"
    assert data["is_primary"] is True

@pytest.mark.anyio
async def test_create_alias_as_user(user_client: AsyncClient, test_asset: Asset):
    payload = {"asset_id": str(test_asset.id), "alias": "Forbidden"}
    response = await user_client.post("/api/v1/asset-aliases/", json=payload)
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.anyio
async def test_create_alias_nonexistent_asset(admin_client: AsyncClient):
    payload = {"asset_id": str(uuid4()), "alias": "NoAsset"}
    response = await admin_client.post("/api/v1/asset-aliases/", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.anyio
async def test_get_all_aliases(admin_client: AsyncClient, test_asset_alias: AssetAlias):
    response = await admin_client.get("/api/v1/asset-aliases/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert any(a["id"] == str(test_asset_alias.id) for a in data)

@pytest.mark.anyio
async def test_get_aliases_for_asset(admin_client: AsyncClient, test_asset: Asset, test_asset_alias: AssetAlias):
    response = await admin_client.get(f"/api/v1/assets/{test_asset.id}/aliases/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["id"] == str(test_asset_alias.id)

@pytest.mark.anyio
async def test_update_alias_as_admin(admin_client: AsyncClient, test_asset_alias: AssetAlias):
    response = await admin_client.put(f"/api/v1/asset-aliases/{test_asset_alias.id}", json={"alias": "Updated Alias"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["alias"] == "Updated Alias"

@pytest.mark.anyio
async def test_delete_alias_as_admin(admin_client: AsyncClient, db_session: AsyncSession, test_asset: Asset):
    alias_to_delete = AssetAlias(asset_id=test_asset.id, alias="ToDelete")
    db_session.add(alias_to_delete)
    await db_session.commit()

    response = await admin_client.delete(f"/api/v1/asset-aliases/{alias_to_delete.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    deleted = await db_session.get(AssetAlias, alias_to_delete.id)
    assert deleted is None