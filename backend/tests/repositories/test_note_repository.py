import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
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

async def test_update_note_raises_on_duplicate_trade_id(note_repo: NoteRepository, db_session: AsyncSession, setup_dependencies):
    """Test that updating a note to a duplicate trade_id raises an exception."""
    folder, trade1, trading_account = setup_dependencies

    # 1. Create the first note via the repository, linked to trade1.
    note1_create_schema = NoteCreate(title="First Note", folder_id=folder.id, trade_id=trade1.id, content={})
    await note_repo.create(note1_create_schema)

    # 2. Create a second trade and a second note.
    trade2 = Trade(id=uuid4(), trading_account_id=trading_account.id)
    db_session.add(trade2)
    await db_session.commit()

    note2_create_schema = NoteCreate(title="Second Note", folder_id=folder.id, trade_id=trade2.id, content={})
    note2_to_update = await note_repo.create(note2_create_schema)

    # 3. Attempt to update the second note to use the first trade's ID. This should fail.
    update_schema = NoteUpdate(trade_id=trade1.id)
    with pytest.raises(HTTPException) as exc_info:
        await note_repo.update(note2_to_update, update_schema)

    assert exc_info.value.status_code == 409
    assert "already exists" in exc_info.value.detail