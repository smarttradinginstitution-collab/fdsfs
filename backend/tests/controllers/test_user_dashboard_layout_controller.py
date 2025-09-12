# backend/tests/controllers/test_user_dashboard_layout_controller.py

import pytest
from httpx import AsyncClient
from uuid import uuid4
from datetime import datetime

from app.main import app
from app.Router.auth import get_current_claims
from app.Schemas.user_dashboard_layout import UserDashboardLayoutRead

# Mock data
FAKE_USER_ID = uuid4()
FAKE_LAYOUT_DATA = [{"i": "0", "x": 0, "y": 0, "w": 2, "h": 2, "component": "TradesList"}]

def mock_get_current_claims_ok():
    """Mock dependency to simulate an authenticated user."""
    return {"sub": str(FAKE_USER_ID)}

@pytest.fixture
def authenticated_client(async_client: AsyncClient):
    """Fixture for an async client with an authenticated user."""
    app.dependency_overrides[get_current_claims] = mock_get_current_claims_ok
    yield async_client
    app.dependency_overrides.clear()

# --------------------------------------------------------------------------
# GET /layout Tests
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_layout_success(authenticated_client: AsyncClient, mocker):
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
    mock_service.return_value.get_layout.return_value = mock_response

    response = await authenticated_client.get("/api/v1/dashboard/layout")

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(FAKE_USER_ID)
    assert data["layout"] == FAKE_LAYOUT_DATA
    mock_service.return_value.get_layout.assert_called_once_with(FAKE_USER_ID)

@pytest.mark.asyncio
async def test_get_layout_not_found(authenticated_client: AsyncClient, mocker):
    """Test case where the layout is not found for the user (404)."""
    mock_service = mocker.patch(
        "app.Controllers.user_dashboard_layout_controller.UserDashboardLayoutService"
    )
    mock_service.return_value.get_layout.return_value = None

    response = await authenticated_client.get("/api/v1/dashboard/layout")

    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_layout_unauthenticated(async_client: AsyncClient):
    """Test that GET /layout requires authentication."""
    # Note: Using the raw async_client without the override
    app.dependency_overrides.clear()
    def mock_get_current_claims_err():
        # This is how the actual dependency behaves on failure
        raise HTTPException(status_code=403, detail="Invalid authentication credentials")

    app.dependency_overrides[get_current_claims] = mock_get_current_claims_err

    response = await async_client.get("/api/v1/dashboard/layout")
    assert response.status_code == 403
    app.dependency_overrides.clear()


# --------------------------------------------------------------------------
# PUT /layout Tests
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_save_layout_success(authenticated_client: AsyncClient, mocker):
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
    mock_service.return_value.save_layout.return_value = mock_response

    payload = {"layout": FAKE_LAYOUT_DATA}
    response = await authenticated_client.put("/api/v1/dashboard/layout", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["layout"] == FAKE_LAYOUT_DATA
    mock_service.return_value.save_layout.assert_called_once()


@pytest.mark.asyncio
async def test_save_layout_invalid_payload(authenticated_client: AsyncClient):
    """Test saving a layout with an invalid payload (422)."""
    # Payload is invalid because `layout` should be a list of objects, not a string.
    payload = {"layout": "invalid data"}
    response = await authenticated_client.put("/api/v1/dashboard/layout", json=payload)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_save_layout_unauthenticated(async_client: AsyncClient):
    """Test that PUT /layout requires authentication."""
    app.dependency_overrides.clear()
    def mock_get_current_claims_err():
        raise HTTPException(status_code=403, detail="Invalid authentication credentials")

    app.dependency_overrides[get_current_claims] = mock_get_current_claims_err

    payload = {"layout": FAKE_LAYOUT_DATA}
    response = await async_client.put("/api/v1/dashboard/layout", json=payload)
    assert response.status_code == 403
    app.dependency_overrides.clear()
