import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from app.Services.discipline_settings_service import DisciplineSettingsService
from app.Schemas.discipline_settings_schema import DisciplineSettingsUpdate

@pytest.fixture
def mock_db_session():
    return AsyncMock()

@pytest.fixture
def mock_settings_repo():
    repo = MagicMock()
    repo.get_by_general_account_id = AsyncMock()
    repo.update = AsyncMock()
    repo.create = AsyncMock()
    return repo

@pytest.fixture
def discipline_settings_service(mock_db_session):
    service = DisciplineSettingsService(mock_db_session)
    # Replace the real repo with the mock
    service.settings_repo = mock_settings_repo()
    return service

@pytest.mark.asyncio
async def test_get_settings_by_general_account(discipline_settings_service, mock_settings_repo):
    general_account_id = uuid4()
    mock_settings_repo.get_by_general_account_id.return_value = {"id": uuid4(), "general_account_id": general_account_id}

    result = await discipline_settings_service.get_settings_by_general_account(general_account_id)

    mock_settings_repo.get_by_general_account_id.assert_called_once_with(general_account_id)
    assert result is not None

@pytest.mark.asyncio
async def test_create_or_update_settings_creates_new_when_not_exist(discipline_settings_service, mock_settings_repo):
    general_account_id = uuid4()
    settings_data = DisciplineSettingsUpdate(trading_days=[1, 2, 3])

    mock_settings_repo.get_by_general_account_id.return_value = None
    mock_settings_repo.create.return_value = {"id": uuid4(), "general_account_id": general_account_id, **settings_data.model_dump()}

    await discipline_settings_service.create_or_update_settings(general_account_id, settings_data)

    mock_settings_repo.get_by_general_account_id.assert_called_once_with(general_account_id)
    mock_settings_repo.create.assert_called_once()
    mock_settings_repo.update.assert_not_called()

@pytest.mark.asyncio
async def test_create_or_update_settings_updates_existing(discipline_settings_service, mock_settings_repo):
    general_account_id = uuid4()
    settings_id = uuid4()
    settings_data = DisciplineSettingsUpdate(trading_days=[1, 2, 3, 4, 5])

    mock_settings_repo.get_by_general_account_id.return_value = MagicMock(id=settings_id)
    mock_settings_repo.update.return_value = {"id": settings_id, "general_account_id": general_account_id, **settings_data.model_dump()}

    await discipline_settings_service.create_or_update_settings(general_account_id, settings_data)

    mock_settings_repo.get_by_general_account_id.assert_called_once_with(general_account_id)
    mock_settings_repo.update.assert_called_once()
    mock_settings_repo.create.assert_not_called()