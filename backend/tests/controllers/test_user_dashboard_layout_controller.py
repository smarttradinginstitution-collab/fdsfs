import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.Infrastructure.db import get_db
from app.Router.auth import get_current_claims
from app.Services.user_dashboard_layout_service import UserDashboardLayoutService, DEFAULT_LAYOUT
from app.Schemas.user_dashboard_layout import UserDashboardLayoutRead, UserDashboardLayoutUpdate, LayoutItemSchema

mock_user_id = uuid4()

@pytest.fixture
def client(mocker):
    """
    Test client fixture that mocks database and authentication dependencies.
    It also mocks the service layer to isolate the controller tests.
    """
    # Mock the service methods before setting up the client
    mocker.patch.object(UserDashboardLayoutService, 'get_layout', new_callable=AsyncMock)
    mocker.patch.object(UserDashboardLayoutService, 'save_layout', new_callable=AsyncMock)

    async def override_get_db():
        yield MagicMock(spec=AsyncSession)

    async def override_get_current_claims():
        return {"sub": str(mock_user_id)}

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_claims] = override_get_current_claims

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def test_get_layout_returns_default_when_none_exists(client):
    """
    Test that the GET endpoint returns the default layout when the service indicates none exists.
    """
    # Configure the mock to return a default layout structure
    default_response = UserDashboardLayoutRead(
        user_id=mock_user_id,
        layout_config=[LayoutItemSchema(**item) for item in DEFAULT_LAYOUT],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    UserDashboardLayoutService.get_layout.return_value = default_response

    response = client.get("/api/v1/users/me/dashboard-layout")

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(mock_user_id)
    assert len(data["layout_config"]) == len(DEFAULT_LAYOUT)
    assert data["layout_config"][0]["i"] == DEFAULT_LAYOUT[0]["i"]
    UserDashboardLayoutService.get_layout.assert_called_once_with(mock_user_id)


def test_save_layout_creates_new_layout(client):
    """
    Test that the PUT endpoint correctly calls the service to create a new layout.
    """
    new_layout_data = {"layout_config": [{"i": "test", "x": 0, "y": 0, "w": 1, "h": 1}]}

    # Configure the mock to return the "saved" layout
    mock_saved_layout = UserDashboardLayoutRead(
        user_id=mock_user_id,
        **new_layout_data,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    UserDashboardLayoutService.save_layout.return_value = mock_saved_layout

    response = client.put("/api/v1/users/me/dashboard-layout", json=new_layout_data)

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(mock_user_id)
    assert data["layout_config"][0]["i"] == "test"

    # Verify the service was called with the correct arguments
    UserDashboardLayoutService.save_layout.assert_called_once()
    call_args = UserDashboardLayoutService.save_layout.call_args[0]
    assert call_args[0] == mock_user_id
    assert isinstance(call_args[1], UserDashboardLayoutUpdate)
    assert call_args[1].layout_config[0].i == "test"


def test_get_layout_returns_saved_layout(client):
    """
    Test that the GET endpoint returns a previously saved layout.
    """
    saved_layout_config = [{"i": "saved_test", "x": 1, "y": 1, "w": 2, "h": 2}]
    mock_saved_layout = UserDashboardLayoutRead(
        user_id=mock_user_id,
        layout_config=saved_layout_config,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    UserDashboardLayoutService.get_layout.return_value = mock_saved_layout

    response = client.get("/api/v1/users/me/dashboard-layout")

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(mock_user_id)
    assert data["layout_config"][0]["i"] == "saved_test"
    UserDashboardLayoutService.get_layout.assert_called_once_with(mock_user_id)
