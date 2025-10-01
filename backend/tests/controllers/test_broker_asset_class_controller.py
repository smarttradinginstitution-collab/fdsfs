import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from fastapi import status

from app.main import app
from app.Models.broker import Broker
from app.Models.asset_class import AssetClass
from app.Models.broker_asset_class import BrokerAssetClass
from app.Models.role import Role
from app.Models.auth_user import AuthUser
from app.Models.user_role import UserRole
from app.Router.auth import get_current_claims

# Re-using fixtures from conftest.py and other test files through pytest's fixture discovery
# For clarity, I'm including fixtures that might be defined in a conftest.py or a shared test file.

@pytest.fixture
async def test_asset_class(db_session: AsyncSession) -> AssetClass:
    """Fixture for a pre-existing asset class."""
    asset_class = AssetClass(name=f"Test Asset Class {uuid4()}")
    db_session.add(asset_class)
    await db_session.commit()
    await db_session.refresh(asset_class)
    return asset_class

# ------------------------------
# Tests for Broker-AssetClass Association
# ------------------------------

@pytest.mark.anyio
async def test_associate_asset_class_as_admin(
    admin_client: AsyncClient, test_broker: Broker, test_asset_class: AssetClass
):
    """Admin can associate an asset class with a broker."""
    response = await admin_client.post(
        f"/api/v1/brokers/{test_broker.id}/asset-classes",
        json={"asset_class_id": str(test_asset_class.id)},
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["broker_id"] == str(test_broker.id)
    assert data["asset_class_id"] == str(test_asset_class.id)

@pytest.mark.anyio
async def test_associate_asset_class_as_user(
    user_client: AsyncClient, test_broker: Broker, test_asset_class: AssetClass
):
    """Regular user cannot associate an asset class."""
    response = await user_client.post(
        f"/api/v1/brokers/{test_broker.id}/asset-classes",
        json={"asset_class_id": str(test_asset_class.id)},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.anyio
async def test_associate_non_existent_asset_class(
    admin_client: AsyncClient, test_broker: Broker
):
    """Cannot associate a non-existent asset class."""
    non_existent_id = uuid4()
    response = await admin_client.post(
        f"/api/v1/brokers/{test_broker.id}/asset-classes",
        json={"asset_class_id": str(non_existent_id)},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.anyio
async def test_associate_asset_class_duplicate(
    admin_client: AsyncClient, test_broker: Broker, test_asset_class: AssetClass
):
    """Cannot associate the same asset class twice."""
    # First association
    await admin_client.post(
        f"/api/v1/brokers/{test_broker.id}/asset-classes",
        json={"asset_class_id": str(test_asset_class.id)},
    )
    # Second attempt
    response = await admin_client.post(
        f"/api/v1/brokers/{test_broker.id}/asset-classes",
        json={"asset_class_id": str(test_asset_class.id)},
    )
    assert response.status_code == status.HTTP_409_CONFLICT

@pytest.mark.anyio
async def test_get_associated_asset_classes(
    admin_client: AsyncClient, db_session: AsyncSession, test_broker: Broker, test_asset_class: AssetClass
):
    """Admin can list associated asset classes."""
    # Create association
    association = BrokerAssetClass(broker_id=test_broker.id, asset_class_id=test_asset_class.id)
    db_session.add(association)
    await db_session.commit()

    response = await admin_client.get(f"/api/v1/brokers/{test_broker.id}/asset-classes")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == str(test_asset_class.id)
    assert data[0]["name"] == test_asset_class.name

@pytest.mark.anyio
async def test_get_associated_asset_classes_as_user(
    user_client: AsyncClient, test_broker: Broker
):
    """Regular user cannot list associated asset classes."""
    response = await user_client.get(f"/api/v1/brokers/{test_broker.id}/asset-classes")
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.anyio
async def test_disassociate_asset_class_as_admin(
    admin_client: AsyncClient, db_session: AsyncSession, test_broker: Broker, test_asset_class: AssetClass
):
    """Admin can disassociate an asset class."""
    # Create association
    association = BrokerAssetClass(broker_id=test_broker.id, asset_class_id=test_asset_class.id)
    db_session.add(association)
    await db_session.commit()

    response = await admin_client.delete(
        f"/api/v1/brokers/{test_broker.id}/asset-classes/{test_asset_class.id}"
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify it's gone
    res = await db_session.get(BrokerAssetClass, association.id)
    assert res is None

@pytest.mark.anyio
async def test_disassociate_asset_class_as_user(
    user_client: AsyncClient, test_broker: Broker, test_asset_class: AssetClass
):
    """Regular user cannot disassociate an asset class."""
    response = await user_client.delete(
        f"/api/v1/brokers/{test_broker.id}/asset-classes/{test_asset_class.id}"
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.anyio
async def test_disassociate_non_existent_association(
    admin_client: AsyncClient, test_broker: Broker, test_asset_class: AssetClass
):
    """Cannot disassociate an asset class that is not associated."""
    response = await admin_client.delete(
        f"/api/v1/brokers/{test_broker.id}/asset-classes/{test_asset_class.id}"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND