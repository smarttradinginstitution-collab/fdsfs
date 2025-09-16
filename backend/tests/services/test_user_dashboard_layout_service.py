# backend/tests/services/test_user_dashboard_layout_service.py

import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.Services.user_dashboard_layout_service import UserDashboardLayoutService
from app.Schemas.user_dashboard_layout import UserDashboardLayoutUpdate, ZonedLayout, WidgetItem
from app.Models.user_dashboard_layout import UserDashboardLayout


@pytest.fixture
def layout_service(db_session: AsyncSession):
    return UserDashboardLayoutService(db=db_session)


@pytest.fixture
def widget_item_data():
    return {
        "i": "a", "x": 0, "y": 0, "w": 1, "h": 2, "component": "TestComponent"
    }

@pytest.fixture
def zoned_layout_data(widget_item_data):
    # Create a WidgetItem to get the default values
    widget_item_with_defaults = WidgetItem(**widget_item_data)
    return {
        "stats": [widget_item_with_defaults.model_dump()],
        "main": [],
        "charts": []
    }

@pytest.fixture
def zoned_layout(zoned_layout_data):
    return ZonedLayout(**zoned_layout_data)


@pytest.mark.asyncio
async def test_get_layout_success_new_format(layout_service: UserDashboardLayoutService, zoned_layout_data):
    # Arrange
    user_id = uuid4()
    layout_service.repo = AsyncMock()

    layout_model = UserDashboardLayout(
        id=uuid4(),
        user_id=user_id,
        layout=zoned_layout_data,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    layout_service.repo.get_by_user_id.return_value = layout_model

    # Act
    result = await layout_service.get_layout(user_id)

    # Assert
    assert result is not None
    assert result.layout.model_dump() == zoned_layout_data
    layout_service.repo.get_by_user_id.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_get_layout_old_format(layout_service: UserDashboardLayoutService):
    # Arrange
    user_id = uuid4()
    layout_service.repo = AsyncMock()
    layout_data = [{"i": "a", "x": 0, "y": 0, "w": 1, "h": 2}] # old list format
    layout_model = UserDashboardLayout(
        id=uuid4(),
        user_id=user_id,
        layout=layout_data,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    layout_service.repo.get_by_user_id.return_value = layout_model

    # Act
    result = await layout_service.get_layout(user_id)

    # Assert
    assert result is None
    layout_service.repo.get_by_user_id.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_get_layout_not_found(layout_service: UserDashboardLayoutService):
    # Arrange
    user_id = uuid4()
    layout_service.repo = AsyncMock()
    layout_service.repo.get_by_user_id.return_value = None

    # Act
    result = await layout_service.get_layout(user_id)

    # Assert
    assert result is None
    layout_service.repo.get_by_user_id.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_save_layout(layout_service: UserDashboardLayoutService, zoned_layout, zoned_layout_data):
    # Arrange
    user_id = uuid4()
    payload = UserDashboardLayoutUpdate(layout=zoned_layout)

    layout_service.repo = AsyncMock()
    upserted_layout = UserDashboardLayout(
        id=uuid4(),
        user_id=user_id,
        layout=zoned_layout_data,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    layout_service.repo.upsert.return_value = upserted_layout

    # Act
    result = await layout_service.save_layout(user_id, payload)

    # Assert
    assert result is not None
    assert result.layout.model_dump() == zoned_layout_data
    layout_service.repo.upsert.assert_called_once_with(user_id, payload)
