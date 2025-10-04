# app/Repositories/note_repository.py
from __future__ import annotations

import datetime
from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.note import Note
from app.Schemas.notebook import NoteCreate, NoteUpdate


class NoteRepository:
    """Repository for Note CRUD operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(
        self, note_id: UUID, include_deleted: bool = False
    ) -> Note | None:
        """Get a note by its ID."""
        stmt = select(Note).where(Note.id == note_id)
        if not include_deleted:
            stmt = stmt.where(Note.deleted_at.is_(None))
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_by_folder_id(self, folder_id: UUID) -> Sequence[Note]:
        """List all notes for a given folder."""
        stmt = (
            select(Note)
            .where(Note.folder_id == folder_id, Note.deleted_at.is_(None))
            .order_by(Note.updated_at.desc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def list_deleted_by_general_account_id(
        self, general_account_id: UUID
    ) -> Sequence[Note]:
        """List all soft-deleted notes for a given general account."""
        stmt = (
            select(Note)
            .where(
                Note.general_account_id == general_account_id,
                Note.deleted_at.isnot(None),
            )
            .order_by(Note.deleted_at.desc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

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
        """Soft delete a note."""
        db_obj.deleted_at = datetime.datetime.now(datetime.timezone.utc)
        self.db.add(db_obj)
        await self.db.commit()

    async def permanently_delete(self, db_obj: Note) -> None:
        """Permanently delete a note from the database."""
        await self.db.delete(db_obj)
        await self.db.commit()