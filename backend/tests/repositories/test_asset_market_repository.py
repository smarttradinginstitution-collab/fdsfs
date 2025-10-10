import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.Repositories.asset_market_repository import AssetMarketRepository
from app.Models.asset_market import AssetMarket
from app.Schemas.asset_market import AssetMarketCreate, AssetMarketUpdate

pytestmark = pytest.mark.anyio

@pytest.fixture
def asset_market_repo(db_session: AsyncSession) -> AssetMarketRepository:
    return AssetMarketRepository(db_session)

async def test_create_asset_market(asset_market_repo: AssetMarketRepository):
    """Test creating a new asset market."""
    market_create = AssetMarketCreate(name="NASDAQ")
    created_market = await asset_market_repo.create(market_create)
    assert created_market is not None
    assert created_market.name == "NASDAQ"
    assert created_market.id is not None

async def test_create_asset_market_raises_on_duplicate_name(
    asset_market_repo: AssetMarketRepository,
):
    """Test that creating an asset market with a duplicate name raises an exception."""
    market_create = AssetMarketCreate(name="NYSE")
    await asset_market_repo.create(market_create)

    with pytest.raises(HTTPException) as exc_info:
        await asset_market_repo.create(market_create)

    assert exc_info.value.status_code == 409
    assert "already exists" in exc_info.value.detail

async def test_update_asset_market(
    asset_market_repo: AssetMarketRepository, db_session: AsyncSession
):
    """Test updating an asset market's name."""
    market = AssetMarket(name="Old Market")
    db_session.add(market)
    await db_session.commit()

    update_schema = AssetMarketUpdate(name="New Market")
    updated_market = await asset_market_repo.update(market.id, update_schema)

    assert updated_market is not None
    assert updated_market.name == "New Market"

async def test_update_asset_market_raises_on_duplicate_name(
    asset_market_repo: AssetMarketRepository, db_session: AsyncSession
):
    """Test that updating an asset market to a duplicate name raises an exception."""
    market1 = AssetMarket(name="Market A")
    market2 = AssetMarket(name="Market B")
    db_session.add_all([market1, market2])
    await db_session.commit()

    update_schema = AssetMarketUpdate(name="Market A")
    with pytest.raises(HTTPException) as exc_info:
        await asset_market_repo.update(market2.id, update_schema)

    assert exc_info.value.status_code == 409
    assert "already exists" in exc_info.value.detail