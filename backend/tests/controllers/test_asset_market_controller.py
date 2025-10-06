import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4, UUID
from fastapi import status

from app.Models.asset_market import AssetMarket
from app.Schemas.asset_market import AssetMarketRead

# Fixture for a pre-existing asset market
@pytest.fixture
async def test_asset_market(db_session: AsyncSession) -> AssetMarket:
    market = AssetMarket(name=f"Test Market {uuid4()}")
    db_session.add(market)
    await db_session.commit()
    await db_session.refresh(market)
    return market

# --- Test Cases ---

@pytest.mark.anyio
async def test_create_asset_market_as_admin(admin_client: AsyncClient):
    """
    Admins should be able to create a new asset market.
    """
    market_name = f"New Market {uuid4()}"
    response = await admin_client.post("/api/v1/asset-markets/", json={"name": market_name})

    assert response.status_code == status.HTTP_201_CREATED
    data = AssetMarketRead(**response.json())
    assert data.name == market_name
    assert isinstance(data.id, UUID)

@pytest.mark.anyio
async def test_create_asset_market_as_user(user_client: AsyncClient):
    """
    Regular users should NOT be able to create an asset market.
    """
    market_name = f"Forbidden Market {uuid4()}"
    response = await user_client.post("/api/v1/asset-markets/", json={"name": market_name})
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.anyio
async def test_create_duplicate_asset_market(admin_client: AsyncClient, test_asset_market: AssetMarket):
    """
    Creating a market with a name that already exists should fail.
    """
    response = await admin_client.post("/api/v1/asset-markets/", json={"name": test_asset_market.name})
    assert response.status_code == status.HTTP_409_CONFLICT

@pytest.mark.anyio
async def test_get_all_asset_markets(user_client: AsyncClient, test_asset_market: AssetMarket):
    """
    Any authenticated user should be able to retrieve all asset markets.
    """
    response = await user_client.get("/api/v1/asset-markets/")
    assert response.status_code == status.HTTP_200_OK

    markets = [AssetMarketRead(**m) for m in response.json()]
    assert isinstance(markets, list)
    assert any(market.id == test_asset_market.id for market in markets)

@pytest.mark.anyio
async def test_get_asset_market_by_id(user_client: AsyncClient, test_asset_market: AssetMarket):
    """
    Any authenticated user should be able to retrieve a specific asset market by its ID.
    """
    response = await user_client.get(f"/api/v1/asset-markets/{test_asset_market.id}")
    assert response.status_code == status.HTTP_200_OK

    market = AssetMarketRead(**response.json())
    assert market.id == test_asset_market.id
    assert market.name == test_asset_market.name

@pytest.mark.anyio
async def test_get_nonexistent_asset_market(user_client: AsyncClient):
    """
    Requesting a non-existent market ID should return a 404 error.
    """
    non_existent_id = uuid4()
    response = await user_client.get(f"/api/v1/asset-markets/{non_existent_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.anyio
async def test_update_asset_market_as_admin(admin_client: AsyncClient, test_asset_market: AssetMarket):
    """
    Admins should be able to update an asset market.
    """
    new_name = f"Updated Market {uuid4()}"
    response = await admin_client.put(f"/api/v1/asset-markets/{test_asset_market.id}", json={"name": new_name})

    assert response.status_code == status.HTTP_200_OK
    data = AssetMarketRead(**response.json())
    assert data.name == new_name
    assert data.id == test_asset_market.id

@pytest.mark.anyio
async def test_update_asset_market_as_user(user_client: AsyncClient, test_asset_market: AssetMarket):
    """
    Regular users should NOT be able to update an asset market.
    """
    new_name = "Forbidden Update"
    response = await user_client.put(f"/api/v1/asset-markets/{test_asset_market.id}", json={"name": new_name})
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.anyio
async def test_update_nonexistent_asset_market(admin_client: AsyncClient):
    """
    Updating a non-existent market ID should return a 404 error.
    """
    non_existent_id = uuid4()
    response = await admin_client.put(f"/api/v1/asset-markets/{non_existent_id}", json={"name": "Won't work"})
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.anyio
async def test_delete_asset_market_as_admin(admin_client: AsyncClient, db_session: AsyncSession):
    """
    Admins should be able to delete an asset market.
    """
    # Create a market to delete
    market_to_delete = AssetMarket(name=f"To Be Deleted {uuid4()}")
    db_session.add(market_to_delete)
    await db_session.commit()
    market_id = market_to_delete.id

    response = await admin_client.delete(f"/api/v1/asset-markets/{market_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify it's gone
    deleted_market = await db_session.get(AssetMarket, market_id)
    assert deleted_market is None

@pytest.mark.anyio
async def test_delete_asset_market_as_user(user_client: AsyncClient, test_asset_market: AssetMarket):
    """
    Regular users should NOT be able to delete an asset market.
    """
    response = await user_client.delete(f"/api/v1/asset-markets/{test_asset_market.id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN