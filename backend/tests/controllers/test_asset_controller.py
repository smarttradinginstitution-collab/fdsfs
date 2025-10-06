import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from fastapi import status

from app.Models.asset import Asset
from app.Models.asset_class import AssetClass
from app.Models.asset_market import AssetMarket

pytestmark = pytest.mark.anyio

# Fixtures for admin_user, regular_user, admin_client, user_client
# are used from tests/controllers/conftest.py

@pytest.fixture
async def test_asset_class(db_session: AsyncSession) -> AssetClass:
    """Fixture for a pre-existing asset class."""
    asset_class = AssetClass(name=f"Test Asset Class {uuid4()}")
    db_session.add(asset_class)
    await db_session.commit()
    return asset_class

@pytest.fixture
async def test_asset_market(db_session: AsyncSession) -> AssetMarket:
    """Fixture for a pre-existing asset market."""
    asset_market = AssetMarket(name=f"Test Market {uuid4()}", code=f"TM{str(uuid4())[:4]}")
    db_session.add(asset_market)
    await db_session.commit()
    return asset_market

@pytest.fixture
async def test_asset(db_session: AsyncSession, test_asset_class: AssetClass, test_asset_market: AssetMarket) -> Asset:
    """Fixture for a pre-existing asset, linked to a class and market."""
    asset = Asset(
        symbol="TEST",
        name="Test Asset",
        asset_class_id=test_asset_class.id,
        asset_market_id=test_asset_market.id
    )
    db_session.add(asset)
    await db_session.commit()
    return asset

# --- Tests for Assets ---

async def test_create_asset_as_admin(admin_client: AsyncClient, test_asset_class: AssetClass, test_asset_market: AssetMarket):
    """Admin should be able to create a new asset."""
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
    assert data["asset_class"]["id"] == str(test_asset_class.id)
    assert data["asset_market"]["id"] == str(test_asset_market.id)

async def test_create_asset_as_user(user_client: AsyncClient, test_asset_class: AssetClass, test_asset_market: AssetMarket):
    """Regular user should not be able to create a new asset."""
    payload = {
        "symbol": "GOOG",
        "name": "Google LLC",
        "asset_class_id": str(test_asset_class.id),
        "asset_market_id": str(test_asset_market.id),
    }
    response = await user_client.post("/api/v1/assets/", json=payload)
    assert response.status_code == status.HTTP_403_FORBIDDEN

async def test_create_asset_nonexistent_market(admin_client: AsyncClient, test_asset_class: AssetClass):
    """Should fail if the asset_market_id does not exist."""
    payload = {
        "symbol": "NOMARKET",
        "name": "No Market",
        "asset_class_id": str(test_asset_class.id),
        "asset_market_id": str(uuid4()),
    }
    response = await admin_client.post("/api/v1/assets/", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "AssetMarket with id" in response.json()["detail"]

async def test_get_all_assets(user_client: AsyncClient, test_asset: Asset):
    """Any authenticated user should be able to list assets."""
    response = await user_client.get("/api/v1/assets/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    found_asset = next((a for a in data if a["id"] == str(test_asset.id)), None)
    assert found_asset is not None
    assert "asset_class" in found_asset
    assert "asset_market" in found_asset
    assert found_asset["asset_class"]["id"] == str(test_asset.asset_class_id)
    assert found_asset["asset_market"]["id"] == str(test_asset.asset_market_id)

async def test_get_asset_by_id(user_client: AsyncClient, test_asset: Asset):
    """Any authenticated user should be able to get an asset by ID."""
    response = await user_client.get(f"/api/v1/assets/{test_asset.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(test_asset.id)
    assert "asset_class" in data
    assert "asset_market" in data
    assert data["asset_class"]["id"] == str(test_asset.asset_class_id)
    assert data["asset_market"]["id"] == str(test_asset.asset_market_id)

async def test_update_asset_market_as_admin(admin_client: AsyncClient, test_asset: Asset, db_session: AsyncSession):
    """Admin should be able to update an asset's market."""
    new_market = AssetMarket(name=f"New Market for Update {uuid4()}", code=f"UPM{str(uuid4())[:3]}")
    db_session.add(new_market)
    await db_session.commit()

    response = await admin_client.put(
        f"/api/v1/assets/{test_asset.id}",
        json={"asset_market_id": str(new_market.id)}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["asset_market"]["id"] == str(new_market.id)

async def test_delete_asset_as_admin(admin_client: AsyncClient, db_session: AsyncSession, test_asset_class: AssetClass, test_asset_market: AssetMarket):
    """Admin should be able to delete an asset."""
    asset_to_delete = Asset(
        symbol="DEL", name="ToDelete", asset_class_id=test_asset_class.id, asset_market_id=test_asset_market.id
    )
    db_session.add(asset_to_delete)
    await db_session.commit()

    response = await admin_client.delete(f"/api/v1/assets/{asset_to_delete.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    deleted = await db_session.get(Asset, asset_to_delete.id)
    assert deleted is None