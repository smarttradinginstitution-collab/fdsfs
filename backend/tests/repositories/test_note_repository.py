import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.Repositories.note_repository import NoteRepository
from app.Models.note import Note
from app.Models.notebook_folder import NotebookFolder
from app.Models.general_account import GeneralAccount
from app.Models.trading_account import TradingAccount
from app.Models.broker import Broker
from app.Models.trade import Trade
from app.Schemas.notebook import NoteCreate, NoteUpdate

pytestmark = pytest.mark.anyio

@pytest.fixture
async def setup_dependencies(db_session: AsyncSession):
    """Fixture to create a general account, a folder, and a trade with all its dependencies."""
    user_id = uuid4()
    general_account = GeneralAccount(id=uuid4(), user_id=user_id, label="test_account")
    broker = Broker(name=f"Test Broker {uuid4()}")
    db_session.add_all([general_account, broker])
    await db_session.commit()

    trading_account = TradingAccount(
        id=uuid4(),
        general_account_id=general_account.id,
        broker_id=broker.id,
        label="Test Trading Acc"
    )
    folder = NotebookFolder(id=uuid4(), name="Test Folder", general_account_id=general_account.id)
    trade = Trade(id=uuid4(), trading_account_id=trading_account.id)
    db_session.add_all([trading_account, folder, trade])
    await db_session.commit()

    return folder, trade, trading_account

@pytest.fixture
def note_repo(db_session: AsyncSession) -> NoteRepository:
    return NoteRepository(db_session)

async def test_create_note_with_unique_trade_id(note_repo: NoteRepository, setup_dependencies):
    """Test creating a note with a unique trade_id."""
    folder, trade, _ = setup_dependencies

    note_create = NoteCreate(
        title="Test Note",
        content={"type": "doc", "content": []},
        folder_id=folder.id,
        trade_id=trade.id
    )
    created_note = await note_repo.create(note_create)

    assert created_note is not None
    assert created_note.title == "Test Note"
    assert created_note.trade_id == trade.id

async def test_create_note_raises_on_duplicate_trade_id(note_repo: NoteRepository, setup_dependencies):
    """Test that creating a note with a duplicate trade_id raises an exception."""
    folder, trade, _ = setup_dependencies

    note_create = NoteCreate(
        title="First Note",
        content={},
        folder_id=folder.id,
        trade_id=trade.id
    )
    await note_repo.create(note_create)

    # Try to create another note with the same trade_id
    note_create_duplicate = NoteCreate(
        title="Second Note",
        content={},
        folder_id=folder.id,
        trade_id=trade.id
    )
    with pytest.raises(HTTPException) as exc_info:
        await note_repo.create(note_create_duplicate)

    assert exc_info.value.status_code == 409
    assert "already exists" in exc_info.value.detail

async def test_update_note_raises_on_duplicate_trade_id(db_session: AsyncSession, setup_dependencies):
    """
    Test that the database UNIQUE constraint on trade_id prevents duplicate linkages.
    This test interacts directly with the session to verify the constraint.
    """
    folder, trade1, trading_account = setup_dependencies

    # 1. ARRANGE: Create and commit the initial state
    note1 = Note(id=uuid4(), title="Note 1", folder_id=folder.id, trade_id=trade1.id, content={}, general_account_id=folder.general_account_id)

    trade2 = Trade(id=uuid4(), trading_account_id=trading_account.id)
    note2 = Note(id=uuid4(), title="Note 2", folder_id=folder.id, trade_id=trade2.id, content={}, general_account_id=folder.general_account_id)

    db_session.add_all([note1, trade2, note2])
    await db_session.commit()

    # 2. ACT: Attempt to create a duplicate link
    note2.trade_id = trade1.id
    db_session.add(note2)

    # 3. ASSERT: The commit must fail due to the unique constraint
    with pytest.raises(IntegrityError):
        await db_session.commit()

    # Clean up the session after a failed commit
    await db_session.rollback()