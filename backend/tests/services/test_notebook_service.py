# backend/tests/services/test_notebook_service.py
import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

from fastapi import HTTPException

from app.Services.notebook_service import NotebookService
from app.Schemas.notebook import NotebookFolderCreate, NoteCreate
from app.Models.notebook_folder import NotebookFolder
from app.Models.note import Note


@pytest.fixture
def mock_db_session():
    """Fixture for a mock database session."""
    return MagicMock()

@pytest.fixture
def mock_folder_repo(mock_db_session):
    """Fixture for a mock NotebookFolderRepository."""
    repo = MagicMock()
    repo.find_by_name_and_account = AsyncMock()
    repo.create = AsyncMock()
    return repo

@pytest.fixture
def mock_note_repo(mock_db_session):
    """Fixture for a mock NoteRepository."""
    repo = MagicMock()
    repo.get_by_trade_id = AsyncMock()
    repo.create = AsyncMock()
    return repo

@pytest.fixture
def mock_general_account_repo(mock_db_session):
    """Fixture for a mock GeneralAccountRepository."""
    repo = MagicMock()
    repo.get_by_user_id = AsyncMock()
    return repo

@pytest.fixture
def notebook_service(
    mock_db_session,
    mock_folder_repo,
    mock_note_repo,
    mock_general_account_repo,
):
    """Fixture for an instance of the NotebookService with mocked repositories."""
    service = NotebookService(db=mock_db_session)
    service.folder_repo = mock_folder_repo
    service.note_repo = mock_note_repo
    service.general_account_repo = mock_general_account_repo
    return service


@pytest.mark.asyncio
async def test_create_folder_raises_conflict_on_duplicate_name(
    notebook_service: NotebookService,
    mock_folder_repo: MagicMock,
    mock_general_account_repo: MagicMock,
):
    """
    Verify that creating a folder with a duplicate name for the same account
    raises a 409 Conflict HTTPException.
    """
    user_id = uuid4()
    general_account_id = uuid4()
    folder_create_data = NotebookFolderCreate(name="Duplicate Folder")

    # Mock dependencies
    mock_general_account_repo.get_by_user_id.return_value = MagicMock(id=general_account_id)
    mock_folder_repo.find_by_name_and_account.return_value = NotebookFolder(
        id=uuid4(), name=folder_create_data.name, general_account_id=general_account_id
    )

    # Assert that a 409 Conflict is raised
    with pytest.raises(HTTPException) as exc_info:
        await notebook_service.create_folder(folder_in=folder_create_data, user_id=user_id)

    assert exc_info.value.status_code == 409
    assert "already exists" in exc_info.value.detail

    # Verify that create was not called
    mock_folder_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_create_note_raises_conflict_on_duplicate_trade_id(
    notebook_service: NotebookService,
    mock_note_repo: MagicMock,
    mock_general_account_repo: MagicMock,
):
    """
    Verify that creating a note with a duplicate trade_id
    raises a 409 Conflict HTTPException.
    """
    user_id = uuid4()
    general_account_id = uuid4()
    trade_id = uuid4()
    note_create_data = NoteCreate(
        title="Test Note",
        content={"type": "doc", "content": [{"type": "paragraph"}]},
        folder_id=uuid4(),
        trade_id=trade_id,
    )

    # Mock dependencies
    mock_general_account_repo.get_by_user_id.return_value = MagicMock(id=general_account_id)
    # Mock the get_folder check to pass
    notebook_service.get_folder = AsyncMock()
    # Simulate finding an existing note with the same trade_id
    mock_note_repo.get_by_trade_id.return_value = Note(
            id=uuid4(), trade_id=trade_id, folder_id=note_create_data.folder_id
    )

    # Assert that a 409 Conflict is raised
    with pytest.raises(HTTPException) as exc_info:
        await notebook_service.create_note(note_in=note_create_data, user_id=user_id)

    assert exc_info.value.status_code == 409
    assert "already exists" in exc_info.value.detail

    # Verify that create was not called
    mock_note_repo.create.assert_not_called()