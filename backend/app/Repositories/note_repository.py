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
                joinedload(Note.trade).options(
                    joinedload(Trade.asset),
                    joinedload(Trade.tags),
                    joinedload(Trade.mistakes),
                    joinedload(Trade.playbook),
                    joinedload(Trade.news_impacts),
                    joinedload(Trade.psychology_states),
                )
            )
            .where(Note.id == note_id)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().first()

    async def list_by_folder_id(self, folder_id: UUID) -> Sequence[Note]:
        """List all notes for a given folder, including related trades and all sub-relationships."""
        stmt = (
            select(Note)
            .options(
                joinedload(Note.trade).options(
                    joinedload(Trade.asset),
                    joinedload(Trade.tags),
                    joinedload(Trade.mistakes),
                    joinedload(Trade.playbook),
                    joinedload(Trade.news_impacts),
                    joinedload(Trade.psychology_states),
                )
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
                joinedload(Note.trade).options(
                    joinedload(Trade.asset),
                    joinedload(Trade.tags),
                    joinedload(Trade.mistakes),
                    joinedload(Trade.playbook),
                    joinedload(Trade.news_impacts),
                    joinedload(Trade.psychology_states),
                )
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
        await self.db.refresh(db_note)
        return db_note

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