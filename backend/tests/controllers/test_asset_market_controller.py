import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from fastapi import status

from app.Models.asset_market import AssetMarket

pytestmark = pytest.mark.anyio


@pytest.fixture
async def test_asset_market(db_session: AsyncSession) -> AssetMarket:
    """Fixture for a pre-existing asset market."""
    asset_market = AssetMarket(
        name=f"Test Market {uuid4()}",
        code=f"TM{str(uuid4())[:4]}"
    )
    db_session.add(asset_market)
    await db_session.commit()
    return asset_market


# Test CREATE operations
async def test_create_asset_market_as_admin(admin_client: AsyncClient):
    market_name = f"New Market {uuid4()}"
    market_code = f"NM{str(uuid4())[:4]}"
    response = await admin_client.post("/api/v1/asset-markets/", json={"name": market_name, "code": market_code})
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == market_name
    assert data["code"] == market_code

async def test_create_asset_market_as_user(user_client: AsyncClient):
    response = await user_client.post("/api/v1/asset-markets/", json={"name": "User Market", "code": "UM"})
    assert response.status_code == status.HTTP_403_FORBIDDEN

async def test_create_asset_market_duplicate_name(admin_client: AsyncClient, test_asset_market: AssetMarket):
    response = await admin_client.post("/api/v1/asset-markets/", json={"name": test_asset_market.name, "code": "UNIQUE_CODE"})
    assert response.status_code == status.HTTP_409_CONFLICT

async def test_create_asset_market_duplicate_code(admin_client: AsyncClient, test_asset_market: AssetMarket):
    response = await admin_client.post("/api/v1/asset-markets/", json={"name": "Unique Name", "code": test_asset_market.code})
    assert response.status_code == status.HTTP_409_CONFLICT


# Test READ operations
async def test_get_all_asset_markets(user_client: AsyncClient, test_asset_market: AssetMarket):
    response = await user_client.get("/api/v1/asset-markets/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert any(am["id"] == str(test_asset_market.id) for am in data)

async def test_get_asset_market_by_id(user_client: AsyncClient, test_asset_market: AssetMarket):
    response = await user_client.get(f"/api/v1/asset-markets/{test_asset_market.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(test_asset_market.id)
    assert data["name"] == test_asset_market.name

async def test_get_nonexistent_asset_market(user_client: AsyncClient):
    non_existent_id = uuid4()
    response = await user_client.get(f"/api/v1/asset-markets/{non_existent_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


# Test UPDATE operations
async def test_update_asset_market_as_admin(admin_client: AsyncClient, test_asset_market: AssetMarket):
    new_name = "Updated Market Name"
    response = await admin_client.put(f"/api/v1/asset-markets/{test_asset_market.id}", json={"name": new_name})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == new_name
    assert data["id"] == str(test_asset_market.id)

async def test_update_asset_market_as_user(user_client: AsyncClient, test_asset_market: AssetMarket):
    response = await user_client.put(f"/api/v1/asset-markets/{test_asset_market.id}", json={"name": "Forbidden Update"})
    assert response.status_code == status.HTTP_403_FORBIDDEN


# Test DELETE operations
async def test_delete_asset_market_as_admin(admin_client: AsyncClient, db_session: AsyncSession):
    market_to_delete = AssetMarket(name="Market to Delete", code="DEL")
    db_session.add(market_to_delete)
    await db_session.commit()

    response = await admin_client.delete(f"/api/v1/asset-markets/{market_to_delete.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify it's gone from the database
    deleted = await db_session.get(AssetMarket, market_to_delete.id)
    assert deleted is None

async def test_delete_asset_market_as_user(user_client: AsyncClient, test_asset_market: AssetMarket):
    response = await user_client.delete(f"/api/v1/asset-markets/{test_asset_market.id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN