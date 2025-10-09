import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.Repositories.broker_repository import BrokerRepository
from app.Models.broker import Broker
from app.Schemas.broker import BrokerCreate, BrokerUpdate

pytestmark = pytest.mark.anyio

@pytest.fixture
def broker_repo(db_session: AsyncSession) -> BrokerRepository:
    return BrokerRepository(db_session)

async def test_create_broker(broker_repo: BrokerRepository):
    """Test creating a new broker."""
    broker_create = BrokerCreate(name="Interactive Brokers")
    created_broker = await broker_repo.create(broker_create.model_dump())
    assert created_broker is not None
    assert created_broker.name == "Interactive Brokers"
    assert created_broker.id is not None

async def test_create_broker_raises_on_duplicate_name(
    broker_repo: BrokerRepository,
):
    """Test that creating a broker with a duplicate name raises an exception."""
    broker_create = BrokerCreate(name="ThinkOrSwim")
    await broker_repo.create(broker_create.model_dump())

    with pytest.raises(HTTPException) as exc_info:
        await broker_repo.create(broker_create.model_dump())

    assert exc_info.value.status_code == 409
    assert "already exists" in exc_info.value.detail

async def test_update_broker(
    broker_repo: BrokerRepository, db_session: AsyncSession
):
    """Test updating a broker's name."""
    broker = Broker(name="Old Broker")
    db_session.add(broker)
    await db_session.commit()

    update_schema = BrokerUpdate(name="New Broker")
    updated_broker = await broker_repo.update(broker, update_schema.model_dump())

    assert updated_broker is not None
    assert updated_broker.name == "New Broker"

async def test_update_broker_raises_on_duplicate_name(
    broker_repo: BrokerRepository, db_session: AsyncSession
):
    """Test that updating a broker to a duplicate name raises an exception."""
    broker1 = Broker(name="Broker A")
    broker2 = Broker(name="Broker B")
    db_session.add_all([broker1, broker2])
    await db_session.commit()

    update_schema = BrokerUpdate(name="Broker A")
    with pytest.raises(HTTPException) as exc_info:
        await broker_repo.update(broker2, update_schema.model_dump())

    assert exc_info.value.status_code == 409
    assert "already exists" in exc_info.value.detail