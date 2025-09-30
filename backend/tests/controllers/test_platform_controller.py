# tests/controllers/test_platform_controller.py
from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.broker import Broker
from app.Models.platform import Platform

pytestmark = pytest.mark.asyncio


# --------------------------------------------------------------------------
# /platforms/
# --------------------------------------------------------------------------

async def test_create_platform_without_brokers(
    async_client: AsyncClient, db_session: AsyncSession
):
    response = await async_client.post(
        "/api/v1/platforms/",
        json={"name": "Test Platform"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Platform"
    assert "id" in data

    # Verify it's in the DB
    db_platform = await db_session.get(Platform, uuid.UUID(data["id"]))
    assert db_platform is not None
    assert db_platform.name == "Test Platform"


async def test_create_platform_with_brokers(
    async_client: AsyncClient, db_session: AsyncSession
):
    # Create some brokers first
    broker1 = Broker(name="Test Broker for Platform 1")
    broker2 = Broker(name="Test Broker for Platform 2")
    db_session.add_all([broker1, broker2])
    await db_session.commit()
    await db_session.refresh(broker1)
    await db_session.refresh(broker2)

    response = await async_client.post(
        "/api/v1/platforms/",
        json={
            "name": "Platform With Brokers",
            "brokers": [str(broker1.id), str(broker2.id)],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Platform With Brokers"

    # Verify associations in the DB
    db_platform = await db_session.get(Platform, uuid.UUID(data["id"]))
    await db_session.refresh(db_platform, attribute_names=['brokers'])
    assert len(db_platform.brokers) == 2
    broker_ids_in_db = {str(b.id) for b in db_platform.brokers}
    assert broker_ids_in_db == {str(broker1.id), str(broker2.id)}


async def test_create_platform_duplicate_name(
    async_client: AsyncClient, db_session: AsyncSession
):
    await async_client.post(
        "/api/v1/platforms/",
        json={"name": "Unique Platform"},
    )
    # Try to create another with the same name
    response = await async_client.post(
        "/api/v1/platforms/",
        json={"name": "Unique Platform"},
    )
    assert response.status_code == 409


async def test_read_platforms(
    async_client: AsyncClient, db_session: AsyncSession
):
    # Create a few platforms
    db_session.add(Platform(name="Platform A"))
    db_session.add(Platform(name="Platform B"))
    await db_session.commit()

    response = await async_client.get("/api/v1/platforms/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


async def test_read_platform(
    async_client: AsyncClient, db_session: AsyncSession
):
    platform = Platform(name="Platform to Read")
    db_session.add(platform)
    await db_session.commit()
    await db_session.refresh(platform)

    response = await async_client.get(
        f"/api/v1/platforms/{platform.id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Platform to Read"
    assert data["id"] == str(platform.id)


async def test_read_platform_summary(
    async_client: AsyncClient, db_session: AsyncSession
):
    broker = Broker(name="Broker for Summary")
    platform = Platform(name="Platform for Summary")
    platform.brokers.append(broker)
    db_session.add_all([broker, platform])
    await db_session.commit()
    await db_session.refresh(platform)
    await db_session.refresh(broker)

    response = await async_client.get(
        f"/api/v1/platforms/{platform.id}/summary"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Platform for Summary"
    assert len(data["brokers"]) == 1
    assert data["brokers"][0]["name"] == "Broker for Summary"


async def test_update_platform_name(
    async_client: AsyncClient, db_session: AsyncSession
):
    platform = Platform(name="Old Name")
    db_session.add(platform)
    await db_session.commit()
    await db_session.refresh(platform)

    response = await async_client.put(
        f"/api/v1/platforms/{platform.id}",
        json={"name": "New Name"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"

    await db_session.refresh(platform)
    assert platform.name == "New Name"


async def test_update_platform_brokers(
    async_client: AsyncClient, db_session: AsyncSession
):
    broker1 = Broker(name="Initial Broker")
    broker2 = Broker(name="Updated Broker")
    platform = Platform(name="Broker Update Platform")
    platform.brokers.append(broker1)
    db_session.add_all([broker1, broker2, platform])
    await db_session.commit()
    await db_session.refresh(platform)
    await db_session.refresh(broker2)

    response = await async_client.put(
        f"/api/v1/platforms/{platform.id}",
        json={"name": platform.name, "brokers": [str(broker2.id)]},
    )
    assert response.status_code == 200

    # Verify in DB
    await db_session.refresh(platform, attribute_names=['brokers'])
    assert len(platform.brokers) == 1
    assert platform.brokers[0].id == broker2.id


async def test_delete_platform(
    async_client: AsyncClient, db_session: AsyncSession
):
    platform = Platform(name="To Be Deleted")
    db_session.add(platform)
    await db_session.commit()
    await db_session.refresh(platform)

    platform_id = str(platform.id)

    response = await async_client.delete(
        f"/api/v1/platforms/{platform_id}"
    )
    assert response.status_code == 200

    # Verify it's gone from the DB
    deleted_platform = await db_session.get(Platform, uuid.UUID(platform_id))
    assert deleted_platform is None