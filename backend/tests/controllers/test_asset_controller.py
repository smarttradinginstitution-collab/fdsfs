import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from fastapi import status

from app.main import app
from sqlalchemy import select
from app.Models.asset import Asset
from app.Models.asset_class import AssetClass
from app.Models.asset_market import AssetMarket
from app.Models.role import Role
from app.Models.auth_user import AuthUser
from app.Models.user_role import UserRole
from app.Router.auth import get_current_claims

# Re-using fixtures from other tests for consistency

@pytest.fixture
async def test_asset_class(db_session: AsyncSession) -> AssetClass:
    asset_class = AssetClass(name=f"Dependency Class {uuid4()}")
    db_session.add(asset_class)
    await db_session.commit()
    return asset_class

@pytest.fixture
async def test_asset_market(db_session: AsyncSession) -> AssetMarket:
    asset_market = AssetMarket(name=f"Dependency Market {uuid4()}")
    db_session.add(asset_market)
    await db_session.commit()
    return asset_market

@pytest.fixture
async def test_asset(db_session: AsyncSession, test_asset_class: AssetClass, test_asset_market: AssetMarket) -> Asset:
    asset = Asset(
        symbol="TEST",
        name="Test Asset",
        asset_class_id=test_asset_class.id,
        asset_market_id=test_asset_market.id,
    )
    db_session.add(asset)
    await db_session.commit()
    await db_session.refresh(asset)
    return asset

# Tests for Assets

@pytest.mark.anyio
async def test_create_asset_as_admin(admin_client: AsyncClient, test_asset_class: AssetClass, test_asset_market: AssetMarket):
    payload = {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "asset_class_id": str(test_asset_class.id),
        "asset_market_id": str(test_asset_market.id),
    }
    response = await admin_client.post("/api/v1/assets/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert data["name"] == "Apple Inc."
    assert data["asset_market"]["id"] == str(test_asset_market.id)
    assert data["asset_class"]["id"] == str(test_asset_class.id)


@pytest.mark.anyio
async def test_create_asset_as_user(user_client: AsyncClient, test_asset_class: AssetClass, test_asset_market: AssetMarket):
    payload = {
        "symbol": "GOOG",
        "name": "Google LLC",
        "asset_class_id": str(test_asset_class.id),
        "asset_market_id": str(test_asset_market.id),
    }
    response = await user_client.post("/api/v1/assets/", json=payload)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_create_asset_symbol_too_long(admin_client: AsyncClient, test_asset_class: AssetClass, test_asset_market: AssetMarket):
    payload = {
        "symbol": "THISISWAYTOOLONG",
        "name": "Long Symbol",
        "asset_class_id": str(test_asset_class.id),
        "asset_market_id": str(test_asset_market.id),
    }
    response = await admin_client.post("/api/v1/assets/", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_create_asset_nonexistent_class(admin_client: AsyncClient, test_asset_market: AssetMarket):
    payload = {
        "symbol": "NOCLASS",
        "name": "No Class",
        "asset_class_id": str(uuid4()),
        "asset_market_id": str(test_asset_market.id),
    }
    response = await admin_client.post("/api/v1/assets/", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.anyio
async def test_create_asset_nonexistent_market(admin_client: AsyncClient, test_asset_class: AssetClass):
    payload = {
        "symbol": "NOMARKET",
        "name": "No Market",
        "asset_class_id": str(test_asset_class.id),
        "asset_market_id": str(uuid4()),
    }
    response = await admin_client.post("/api/v1/assets/", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.anyio
async def test_get_all_assets(user_client: AsyncClient, test_asset: Asset):
    response = await user_client.get("/api/v1/assets/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert any(a["id"] == str(test_asset.id) for a in data)
    # Check that nested data is loaded
    assert "asset_market" in data[0]
    assert "asset_class" in data[0]

@pytest.mark.anyio
async def test_get_asset_by_id(user_client: AsyncClient, test_asset: Asset):
    response = await user_client.get(f"/api/v1/assets/{test_asset.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(test_asset.id)
    assert data["asset_market"]["id"] == str(test_asset.asset_market_id)
    assert data["asset_class"]["id"] == str(test_asset.asset_class_id)

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
async def test_delete_asset_as_admin(admin_client: AsyncClient, db_session: AsyncSession, test_asset_class: AssetClass, test_asset_market: AssetMarket):
    asset_to_delete = Asset(
        symbol="DEL",
        name="ToDelete",
        asset_class_id=test_asset_class.id,
        asset_market_id=test_asset_market.id,
    )
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