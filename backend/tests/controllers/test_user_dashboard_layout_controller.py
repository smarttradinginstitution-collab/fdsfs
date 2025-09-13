# backend/tests/controllers/test_user_dashboard_layout_controller.py

import pytest
from httpx import AsyncClient
from uuid import uuid4
from datetime import datetime
from typing import AsyncGenerator
from unittest.mock import AsyncMock

from app.main import app
from app.Router.auth import get_current_claims
from app.Schemas.user_dashboard_layout import UserDashboardLayoutRead
from app.Infrastructure.db import get_db
from fastapi import HTTPException

# Mock data
FAKE_USER_ID = uuid4()
FAKE_LAYOUT_DATA = {
    "stats": [],
    "main": [{"i": "0", "x": 0, "y": 0, "w": 2, "h": 2, "component": "TradesList", "isDraggable": None, "isResizable": None, "static": None}],
    "charts": []
}

def mock_get_current_claims_ok():
    """Mock dependency to simulate an authenticated user."""
    return {"sub": str(FAKE_USER_ID)}

@pytest.fixture
def authenticated_user():
    """Fixture to mock an authenticated user and the database."""
    async def override_get_db():
        yield None

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_claims] = mock_get_current_claims_ok
    yield
    app.dependency_overrides.clear()

# --------------------------------------------------------------------------
# GET /layout Tests
# --------------------------------------------------------------------------

@pytest.mark.anyio
async def test_get_layout_success(async_client: AsyncClient, authenticated_user, mocker):
    """Test successful retrieval of a dashboard layout."""
    mock_response = UserDashboardLayoutRead(
        id=uuid4(),
        user_id=FAKE_USER_ID,
        layout=FAKE_LAYOUT_DATA,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    mock_service = mocker.patch(
        "app.Controllers.user_dashboard_layout_controller.UserDashboardLayoutService"
    )
    mock_service.return_value.get_layout = AsyncMock(return_value=mock_response)

    response = await async_client.get("/api/v1/dashboard/layout")

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(FAKE_USER_ID)
    assert data["layout"] == FAKE_LAYOUT_DATA
    mock_service.return_value.get_layout.assert_called_once_with(FAKE_USER_ID)

@pytest.mark.anyio
async def test_get_layout_not_found(async_client: AsyncClient, authenticated_user, mocker):
    """Test case where the layout is not found for the user (404)."""
    mock_service = mocker.patch(
        "app.Controllers.user_dashboard_layout_controller.UserDashboardLayoutService"
    )
    mock_service.return_value.get_layout = AsyncMock(return_value=None)

    response = await async_client.get("/api/v1/dashboard/layout")

    assert response.status_code == 404

@pytest.mark.anyio
async def test_get_layout_unauthenticated(async_client: AsyncClient):
    """Test that GET /layout requires authentication."""
    def mock_get_current_claims_err():
        raise HTTPException(status_code=403, detail="Invalid authentication credentials")

    app.dependency_overrides[get_current_claims] = mock_get_current_claims_err
    response = await async_client.get("/api/v1/dashboard/layout")
    assert response.status_code == 403
    app.dependency_overrides.clear()


# --------------------------------------------------------------------------
# PUT /layout Tests
# --------------------------------------------------------------------------

@pytest.mark.anyio
async def test_save_layout_success(async_client: AsyncClient, authenticated_user, mocker):
    """Test successful creation/update of a dashboard layout."""
    mock_response = UserDashboardLayoutRead(
        id=uuid4(),
        user_id=FAKE_USER_ID,
        layout=FAKE_LAYOUT_DATA,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    mock_service = mocker.patch(
        "app.Controllers.user_dashboard_layout_controller.UserDashboardLayoutService"
    )
    mock_service.return_value.save_layout = AsyncMock(return_value=mock_response)

    payload = {"layout": FAKE_LAYOUT_DATA}
    response = await async_client.put("/api/v1/dashboard/layout", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["layout"] == FAKE_LAYOUT_DATA
    mock_service.return_value.save_layout.assert_called_once()


@pytest.mark.anyio
async def test_save_layout_invalid_payload(async_client: AsyncClient, authenticated_user):
    """Test saving a layout with an invalid payload (422)."""
    # Payload is invalid because `layout` should be a list of objects, not a string.
    payload = {"layout": "invalid data"}
    response = await async_client.put("/api/v1/dashboard/layout", json=payload)
    assert response.status_code == 422

@pytest.mark.anyio
async def test_save_layout_unauthenticated(async_client: AsyncClient):
    """Test that PUT /layout requires authentication."""
    def mock_get_current_claims_err():
        raise HTTPException(status_code=403, detail="Invalid authentication credentials")

    app.dependency_overrides[get_current_claims] = mock_get_current_claims_err
    payload = {"layout": FAKE_LAYOUT_DATA}
    response = await async_client.put("/api/v1/dashboard/layout", json=payload)
    assert response.status_code == 403
    app.dependency_overrides.clear()
