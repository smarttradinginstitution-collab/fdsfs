import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from uuid import uuid4
from datetime import datetime, timezone

from app.main import app
from app.Infrastructure.db import get_db
from app.Services.user_dashboard_layout_service import DEFAULT_LAYOUT
from app.Schemas.user_dashboard_layout import UserDashboardLayoutRead, UserDashboardLayoutUpdate

# --- Mock Data ---
mock_user_id = uuid4()
mock_layout_data = {"layout": [{"i": "a", "x": 0, "y": 0, "w": 1, "h": 1, "component": "TestWidget"}]}

# This is the Pydantic model that the service is expected to return
mock_read_schema_layout = UserDashboardLayoutRead(
    id=1,
    user_id=mock_user_id,
    layout=mock_layout_data["layout"],
    created_at=datetime.now(timezone.utc),
    updated_at=datetime.now(timezone.utc)
)

# --- Pytest Fixture for Test Client ---
@pytest.fixture
def client():
    """
    Creates a TestClient for the FastAPI app, overriding the get_db dependency.
    """
    async def override_get_db():
        yield None  # We don't need a real DB session as the service is mocked

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# --- Test Cases ---

@patch('app.Controllers.user_dashboard_layout_controller.UserDashboardLayoutService', autospec=True)
def test_get_layout_found(MockUserDashboardLayoutService, client):
    """
    Tests GET /api/v1/dashboard/layout when a layout exists for the user.
    It mocks the service layer to isolate the controller's logic.
    """
    # Arrange: Configure the mock service instance to return a specific layout
    mock_service_instance = MockUserDashboardLayoutService.return_value
    mock_service_instance.get_layout_for_user = AsyncMock(return_value=mock_read_schema_layout)

    # Act: Make the request
    response = client.get(f"/api/v1/dashboard/layout?user_id={mock_user_id}")

    # Assert: Check the response and that the service was called correctly
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["user_id"] == str(mock_user_id)
    assert response_data["layout"] == mock_read_schema_layout.layout
    mock_service_instance.get_layout_for_user.assert_called_once_with(mock_user_id)

@patch('app.Controllers.user_dashboard_layout_controller.UserDashboardLayoutService', autospec=True)
def test_get_layout_not_found(MockUserDashboardLayoutService, client):
    """
    Tests GET /api/v1/dashboard/layout when no layout exists.
    The service should return the default layout.
    """
    # Arrange: Configure the mock service to return a default layout response
    default_response = UserDashboardLayoutRead(user_id=mock_user_id, layout=DEFAULT_LAYOUT)
    mock_service_instance = MockUserDashboardLayoutService.return_value
    mock_service_instance.get_layout_for_user = AsyncMock(return_value=default_response)

    # Act
    response = client.get(f"/api/v1/dashboard/layout?user_id={mock_user_id}")

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["user_id"] == str(mock_user_id)
    assert response_data["layout"] == DEFAULT_LAYOUT
    assert response_data["id"] is None
    mock_service_instance.get_layout_for_user.assert_called_once_with(mock_user_id)

@patch('app.Controllers.user_dashboard_layout_controller.UserDashboardLayoutService', autospec=True)
def test_update_layout(MockUserDashboardLayoutService, client):
    """
    Tests PUT /api/v1/dashboard/layout to save a new layout.
    It mocks the service and verifies it's called with the correct data.
    """
    # Arrange
    mock_service_instance = MockUserDashboardLayoutService.return_value
    mock_service_instance.save_layout_for_user = AsyncMock(return_value=mock_read_schema_layout)

    # Act
    response = client.put(
        f"/api/v1/dashboard/layout?user_id={mock_user_id}",
        json=mock_layout_data
    )

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["user_id"] == str(mock_user_id)

    # Verify the service method was called correctly
    mock_service_instance.save_layout_for_user.assert_called_once()
    call_args = mock_service_instance.save_layout_for_user.call_args[0]
    assert call_args[0] == mock_user_id
    assert isinstance(call_args[1], UserDashboardLayoutUpdate)
    assert call_args[1].layout == mock_layout_data["layout"]
