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
# /platforms/ - ADMIN-only routes (POST, PUT, DELETE)
# --------------------------------------------------------------------------

async def test_create_platform_as_admin(
    admin_async_client: AsyncClient, db_session: AsyncSession
):
    response = await admin_async_client.post(
        "/api/v1/platforms/",
        json={"name": "Test Platform by Admin"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Platform by Admin"
    db_platform = await db_session.get(Platform, uuid.UUID(data["id"]))
    assert db_platform is not None

async def test_create_platform_as_non_admin(
    async_client: AsyncClient, db_session: AsyncSession
):
    response = await async_client.post(
        "/api/v1/platforms/",
        json={"name": "Attempt by Non-Admin"},
    )
    assert response.status_code == 403

async def test_update_platform_as_admin(
    admin_async_client: AsyncClient, db_session: AsyncSession
):
    platform = Platform(name="Old Name")
    db_session.add(platform)
    await db_session.commit()
    await db_session.refresh(platform)

    response = await admin_async_client.put(
        f"/api/v1/platforms/{platform.id}",
        json={"name": "New Name by Admin"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name by Admin"

async def test_update_platform_as_non_admin(
    async_client: AsyncClient, db_session: AsyncSession
):
    platform = Platform(name="Non-Admin Update Test")
    db_session.add(platform)
    await db_session.commit()
    await db_session.refresh(platform)

    response = await async_client.put(
        f"/api/v1/platforms/{platform.id}",
        json={"name": "This should fail"},
    )
    assert response.status_code == 403

async def test_delete_platform_as_admin(
    admin_async_client: AsyncClient, db_session: AsyncSession
):
    platform = Platform(name="To Be Deleted by Admin")
    db_session.add(platform)
    await db_session.commit()
    await db_session.refresh(platform)
    platform_id = platform.id

    response = await admin_async_client.delete(f"/api/v1/platforms/{platform_id}")
    assert response.status_code == 200

    deleted_platform = await db_session.get(Platform, platform_id)
    assert deleted_platform is None

async def test_delete_platform_as_non_admin(
    async_client: AsyncClient, db_session: AsyncSession
):
    platform = Platform(name="Non-Admin Delete Test")
    db_session.add(platform)
    await db_session.commit()
    await db_session.refresh(platform)

    response = await async_client.delete(f"/api/v1/platforms/{platform.id}")
    assert response.status_code == 403

# --------------------------------------------------------------------------
# /platforms/ - Public READ routes
# --------------------------------------------------------------------------

async def test_read_platforms_as_non_admin(
    async_client: AsyncClient, db_session: AsyncSession
):
    db_session.add(Platform(name="Platform A"))
    db_session.add(Platform(name="Platform B"))
    await db_session.commit()

    response = await async_client.get("/api/v1/platforms/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

async def test_read_platform_as_non_admin(
    async_client: AsyncClient, db_session: AsyncSession
):
    platform = Platform(name="Platform to Read")
    db_session.add(platform)
    await db_session.commit()
    await db_session.refresh(platform)

    response = await async_client.get(f"/api/v1/platforms/{platform.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Platform to Read"

async def test_read_platform_summary_as_non_admin(
    async_client: AsyncClient, db_session: AsyncSession
):
    broker = Broker(name="Broker for Summary")
    platform = Platform(name="Platform for Summary", brokers=[broker])
    db_session.add(platform)
    await db_session.commit()
    await db_session.refresh(platform)

    response = await async_client.get(f"/api/v1/platforms/{platform.id}/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Platform for Summary"
    assert len(data["brokers"]) == 1
    assert data["brokers"][0]["name"] == "Broker for Summary"