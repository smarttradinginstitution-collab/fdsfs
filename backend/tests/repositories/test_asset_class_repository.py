import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

# Schemas
from app.Schemas.asset_class import AssetClassCreate, AssetClassUpdate

# Models needed for the test
from app.Models.auth_user import AuthUser
from app.Models.general_account import GeneralAccount
from app.Models.trading_account import TradingAccount
from app.Models.broker import Broker
from app.Models.asset_class import AssetClass
from app.Models.asset_market import AssetMarket
from app.Models.asset import Asset
from app.Models.trade import Trade
from app.Models.broker_asset_class import BrokerAssetClass

# The repository to be tested
from app.Repositories.asset_class_repository import AssetClassRepository


pytestmark = pytest.mark.anyio


@pytest.fixture
def asset_class_repo(db_session: AsyncSession) -> AssetClassRepository:
    return AssetClassRepository(db_session)


async def test_create_asset_class(asset_class_repo: AssetClassRepository):
    """Test creating a new asset class."""
    asset_class_create = AssetClassCreate(name="Stocks")
    created_asset_class = await asset_class_repo.create(asset_class_create)
    assert created_asset_class is not None
    assert created_asset_class.name == "Stocks"
    assert created_asset_class.id is not None


async def test_create_asset_class_raises_on_duplicate_name(
    asset_class_repo: AssetClassRepository,
):
    """Test that creating an asset class with a duplicate name raises an exception."""
    # Create the first asset class
    asset_class_create = AssetClassCreate(name="Forex")
    await asset_class_repo.create(asset_class_create)

    # Try to create another with the same name
    with pytest.raises(HTTPException) as exc_info:
        await asset_class_repo.create(asset_class_create)

    assert exc_info.value.status_code == 409
    assert "already exists" in exc_info.value.detail


async def test_update_asset_class(
    asset_class_repo: AssetClassRepository, db_session: AsyncSession
):
    """Test updating an asset class's name."""
    asset_class = AssetClass(name="Bonds")
    db_session.add(asset_class)
    await db_session.commit()

    update_schema = AssetClassUpdate(name="Government Bonds")
    updated_asset_class = await asset_class_repo.update(asset_class.id, update_schema)

    assert updated_asset_class is not None
    assert updated_asset_class.name == "Government Bonds"


async def test_update_asset_class_raises_on_duplicate_name(
    asset_class_repo: AssetClassRepository, db_session: AsyncSession
):
    """Test that updating an asset class to a duplicate name raises an exception."""
    # Create two asset classes
    asset_class1 = AssetClass(name="Crypto")
    asset_class2 = AssetClass(name="NFTs")
    db_session.add_all([asset_class1, asset_class2])
    await db_session.commit()

    # Try to update the second to have the same name as the first
    update_schema = AssetClassUpdate(name="Crypto")
    with pytest.raises(HTTPException) as exc_info:
        await asset_class_repo.update(asset_class2.id, update_schema)

    assert exc_info.value.status_code == 409
    assert "already exists" in exc_info.value.detail


@pytest.mark.anyio
async def test_delete_asset_class_cascades(db_session: AsyncSession):
    """
    Test that deleting an AssetClass correctly cascades deletions and updates related entities.
    """
    # 1. Setup: Create all necessary related entities with unique constraints

    # User and accounts
    user_id = uuid4()
    user = AuthUser(id=user_id, email=f"user_{user_id}@test.com")
    db_session.add(user)
    await db_session.flush()

    general_account = GeneralAccount(user_id=user.id, label="Test General Account")
    db_session.add(general_account)
    await db_session.flush()

    # Broker with a unique name
    broker_name = f"Test Broker {uuid4()}"
    broker = Broker(name=broker_name)
    db_session.add(broker)
    await db_session.flush()

    trading_account = TradingAccount(
        general_account_id=general_account.id,
        broker_id=broker.id,
        label="Test Trading Account"
    )
    db_session.add(trading_account)
    await db_session.flush()

    # AssetClass with a unique name
    asset_class_name = f"Test Class {uuid4()}"
    asset_class = AssetClass(name=asset_class_name)
    db_session.add(asset_class)
    await db_session.flush()

    # Link Broker and AssetClass
    broker_asset_class = BrokerAssetClass(broker_id=broker.id, asset_class_id=asset_class.id)
    db_session.add(broker_asset_class)
    await db_session.flush()

    # AssetMarket
    asset_market = AssetMarket(name=f"Cascade Test Market {uuid4()}")
    db_session.add(asset_market)
    await db_session.flush()

    # Asset
    asset = Asset(
        name="Test Asset",
        asset_class_id=asset_class.id,
        asset_market_id=asset_market.id,
    )
    db_session.add(asset)
    await db_session.flush()

    # Trade
    trade = Trade(asset_id=asset.id, trading_account_id=trading_account.id)
    db_session.add(trade)
    await db_session.commit() # Commit to make sure everything is in the DB before deletion

    # 2. Action: Delete the AssetClass using its repository
    repo = AssetClassRepository(db_session)
    await repo.delete(asset_class.id)
    await db_session.commit()

    # 3. Verification: Check that everything was deleted or updated as expected

    # Verify AssetClass is deleted
    deleted_asset_class = await db_session.get(AssetClass, asset_class.id)
    assert deleted_asset_class is None, "AssetClass should be deleted"

    # Verify associated Asset is deleted
    deleted_asset = await db_session.get(Asset, asset.id)
    assert deleted_asset is None, "Associated Asset should be deleted"

    # Verify associated BrokerAssetClass is deleted
    deleted_broker_asset_class = await db_session.get(BrokerAssetClass, broker_asset_class.id)
    assert deleted_broker_asset_class is None, "Associated BrokerAssetClass should be deleted"

    # Verify Trade's asset_id is set to NULL
    updated_trade = await db_session.get(Trade, trade.id)
    assert updated_trade is not None, "Trade should not be deleted"
    assert updated_trade.asset_id is None, "Trade.asset_id should be set to NULL"