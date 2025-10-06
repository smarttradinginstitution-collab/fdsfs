# app/Repositories/note_repository.py
from __future__ import annotations

from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.Models.note import Note
from app.Models.trade import Trade # Import the Trade model
from app.Schemas.notebook import NoteCreate, NoteUpdate


class NoteRepository:
    """Repository for Note CRUD operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, note_id: UUID) -> Note | None:
        """Get a note by its ID, including its related trade and all sub-relationships."""
        stmt = (
            select(Note)
            .options(
                joinedload(Note.trade).joinedload(Trade.asset),
                joinedload(Note.trade).joinedload(Trade.tags),
                joinedload(Note.trade).joinedload(Trade.mistakes),
                joinedload(Note.trade).joinedload(Trade.playbook),
                joinedload(Note.trade).joinedload(Trade.news_impacts),
                joinedload(Note.trade).joinedload(Trade.psychology_states),
            )
            .where(Note.id == note_id)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().first()

    async def get_by_trade_id(self, trade_id: UUID) -> Note | None:
        """Get a note by its trade_id."""
        stmt = select(Note).where(Note.trade_id == trade_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_by_folder_id(self, folder_id: UUID) -> Sequence[Note]:
        """List all notes for a given folder, including related trades and all sub-relationships."""
        stmt = (
            select(Note)
            .options(
                joinedload(Note.trade).joinedload(Trade.asset),
                joinedload(Note.trade).joinedload(Trade.tags),
                joinedload(Note.trade).joinedload(Trade.mistakes),
                joinedload(Note.trade).joinedload(Trade.playbook),
                joinedload(Note.trade).joinedload(Trade.news_impacts),
                joinedload(Note.trade).joinedload(Trade.psychology_states),
            )
            .where(Note.folder_id == folder_id)
            .order_by(Note.updated_at.desc())
        )
        res = await self.db.execute(stmt)
        return res.unique().scalars().all()

    async def list_by_general_account_id(self, general_account_id: UUID) -> Sequence[Note]:
        """List all notes for a given general account, including related trades and all sub-relationships."""
        stmt = (
            select(Note)
            .options(
                joinedload(Note.trade).joinedload(Trade.asset),
                joinedload(Note.trade).joinedload(Trade.tags),
                joinedload(Note.trade).joinedload(Trade.mistakes),
                joinedload(Note.trade).joinedload(Trade.playbook),
                joinedload(Note.trade).joinedload(Trade.news_impacts),
                joinedload(Note.trade).joinedload(Trade.psychology_states),
            )
            .where(Note.general_account_id == general_account_id)
            .order_by(Note.updated_at.desc())
        )
        res = await self.db.execute(stmt)
        return res.unique().scalars().all()

    async def create(self, note_in: NoteCreate, general_account_id: UUID) -> Note:
        """Create a new note."""
        db_note = Note(
            **note_in.model_dump(), general_account_id=general_account_id
        )
        self.db.add(db_note)
        await self.db.commit()
        # After committing, the note has an ID. We need to fetch it again
        # using our eager-loading method to ensure all relationships are loaded
        # before returning it to the service layer. This prevents lazy-loading errors.
        newly_created_note = await self.get_by_id(db_note.id)
        if not newly_created_note:
             # This should theoretically never happen, but it's a safeguard.
             raise Exception("Failed to fetch newly created note.")
        return newly_created_note

    async def update(self, db_obj: Note, obj_in: NoteUpdate) -> Note:
        """Update an existing note."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: Note) -> None:
        """Delete a note."""
        await self.db.delete(db_obj)
        await self.db.commit()