# backend/tests/services/test_playbook_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.Services.playbook_service import PlaybookService

pytestmark = pytest.mark.anyio

@pytest.fixture
def mock_db_session():
    session = AsyncMock()
    # db.add is synchronous, so we mock it with a standard MagicMock
    # to avoid RuntimeWarning about an un-awaited coroutine.
    session.add = MagicMock()
    return session

@pytest.fixture
def playbook_service(mock_db_session):
    service = PlaybookService(db=mock_db_session)
    service.playbook_repo = AsyncMock()
    service.trade_repo = AsyncMock()
    return service

async def test_delete_playbook_and_cleanup_trades(playbook_service: PlaybookService):
    # 1. Setup
    playbook_id = uuid4()
    playbook_to_delete = MagicMock()
    playbook_to_delete.id = playbook_id

    # Create mock trades that are associated with the playbook
    trade1 = MagicMock()
    trade1.playbook_id = playbook_id

    trade2 = MagicMock()
    trade2.playbook_id = playbook_id

    # Mock the repository calls
    playbook_service.trade_repo.list_by_playbook_id.return_value = [trade1, trade2]
    playbook_service.playbook_repo.delete.return_value = None

    # 2. Execute
    await playbook_service.delete_playbook_and_cleanup_trades(playbook_to_delete)

    # 3. Assert
    # Verify that the trades were cleaned up
    assert trade1.playbook_id is None
    assert trade2.playbook_id is None

    # Verify that the correct methods were called
    playbook_service.trade_repo.list_by_playbook_id.assert_called_once_with(playbook_id)
    assert playbook_service.db.add.call_count == 2
    playbook_service.playbook_repo.delete.assert_called_once_with(db_obj=playbook_to_delete)
    playbook_service.db.commit.assert_called_once()
