import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.playbook import Playbook
from app.Repositories.playbook_repository import PlaybookRepository

@pytest.mark.anyio
async def test_upsert_by_name_creates_new_playbook_if_not_exists():
    """
    Test that upsert_by_name creates a new playbook if it doesn't exist.
    """
    mock_session = AsyncMock(spec=AsyncSession)

    # Mock for the SELECT query
    mock_select_result = MagicMock()
    mock_select_result.scalars.return_value.first.return_value = None

    # Mock for the INSERT query
    new_playbook = Playbook(id=uuid4(), general_account_id=uuid4(), name="New Playbook", color="#FF0000")
    mock_insert_result = MagicMock()
    mock_insert_result.scalar_one.return_value = new_playbook

    # When execute is called, return the appropriate mock result
    mock_session.execute.side_effect = [
        mock_select_result,
        mock_insert_result,
    ]

    repo = PlaybookRepository(mock_session)
    result = await repo.upsert_by_name(general_account_id=new_playbook.general_account_id, name=new_playbook.name, color=new_playbook.color)

    assert result == new_playbook
    assert mock_session.execute.call_count == 2
    assert mock_session.flush.call_count == 1

@pytest.mark.anyio
async def test_upsert_by_name_updates_color_if_different():
    """
    Test that upsert_by_name updates the color of an existing playbook if the color is different.
    """
    mock_session = AsyncMock(spec=AsyncSession)

    general_account_id = uuid4()
    playbook_name = "Existing Playbook"
    old_color = "#0000FF"
    new_color = "#FF0000"

    existing_playbook = Playbook(id=uuid4(), general_account_id=general_account_id, name=playbook_name, color=old_color)

    mock_select_result = MagicMock()
    mock_select_result.scalars.return_value.first.return_value = existing_playbook
    mock_session.execute.return_value = mock_select_result

    repo = PlaybookRepository(mock_session)
    result = await repo.upsert_by_name(general_account_id=general_account_id, name=playbook_name, color=new_color)

    assert result.color == new_color
    assert mock_session.flush.call_count == 1

@pytest.mark.anyio
async def test_upsert_by_name_does_not_update_if_color_is_same():
    """
    Test that upsert_by_name does not update an existing playbook if the color is the same.
    """
    mock_session = AsyncMock(spec=AsyncSession)

    general_account_id = uuid4()
    playbook_name = "Existing Playbook"
    same_color = "#0000FF"

    existing_playbook = Playbook(id=uuid4(), general_account_id=general_account_id, name=playbook_name, color=same_color)

    mock_select_result = MagicMock()
    mock_select_result.scalars.return_value.first.return_value = existing_playbook
    mock_session.execute.return_value = mock_select_result

    repo = PlaybookRepository(mock_session)
    result = await repo.upsert_by_name(general_account_id=general_account_id, name=playbook_name, color=same_color)

    assert result.color == same_color
    assert mock_session.flush.call_count == 0

@pytest.mark.anyio
async def test_list_playbooks_by_general_account():
    """
    Test that list_playbooks_by_general_account returns a sequence of playbooks for a given general account.
    """
    mock_session = AsyncMock(spec=AsyncSession)
    general_account_id = uuid4()

    playbooks = [
        Playbook(id=uuid4(), general_account_id=general_account_id, name="Playbook 1", color="#FF0000"),
        Playbook(id=uuid4(), general_account_id=general_account_id, name="Playbook 2", color="#00FF00"),
    ]

    mock_select_result = MagicMock()
    mock_select_result.scalars.return_value.all.return_value = playbooks
    mock_session.execute.return_value = mock_select_result

    repo = PlaybookRepository(mock_session)
    result = await repo.list_playbooks_by_general_account_id(general_account_id=general_account_id)

    assert len(result) == 2
    assert result[0].name == "Playbook 1"
    assert result[1].name == "Playbook 2"