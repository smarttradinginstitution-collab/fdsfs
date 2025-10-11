# app/Repositories/note_repository.py
from __future__ import annotations

from typing import Sequence
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.Models.note import Note
from app.Models.notebook_folder import NotebookFolder
from app.Models.trade import Trade
from app.Models.note_template import NoteTemplate
from app.Schemas.notebook import NoteCreate, NoteUpdate


class NoteRepository:
    """Repository for Note CRUD operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def _get_base_query(self):
        """
        Constructs a base query for notes with all necessary relationships
        eagerly loaded to prevent lazy-loading issues in async contexts.
        """
        return select(Note).options(
            joinedload(Note.folder),
            joinedload(Note.trade).joinedload(Trade.asset),
            joinedload(Note.trade).joinedload(Trade.tags),
            joinedload(Note.trade).joinedload(Trade.mistakes),
            joinedload(Note.trade).joinedload(Trade.playbook),
            joinedload(Note.trade).joinedload(Trade.news_impacts),
            joinedload(Note.trade).joinedload(Trade.psychology_states),
            selectinload(Note.templates),
        )

    async def get_by_id(self, note_id: UUID) -> Note | None:
        """Get a note by its ID, including all relationships."""
        stmt = self._get_base_query().where(Note.id == note_id)
        result = await self.db.execute(stmt)
        return result.unique().scalars().first()

    async def get_by_trade_id(self, trade_id: UUID) -> Note | None:
        """Get a note by its trade_id, including all relationships."""
        stmt = self._get_base_query().where(Note.trade_id == trade_id)
        result = await self.db.execute(stmt)
        return result.unique().scalars().first()

    async def find_by_title_and_account(
        self, title: str, general_account_id: UUID
    ) -> Note | None:
        """
        Finds a note by its exact title for a specific general account,
        including all relationships.
        """
        stmt = (
            self._get_base_query()
            .join(Note.folder)
            .where(
                Note.title == title,
                NotebookFolder.general_account_id == general_account_id,
            )
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().first()

    async def list_by_folder_id(self, folder_id: UUID) -> Sequence[Note]:
        """List all notes for a given folder, including all relationships."""
        stmt = (
            self._get_base_query()
            .where(Note.folder_id == folder_id)
            .order_by(Note.updated_at.desc())
        )
        res = await self.db.execute(stmt)
        return res.unique().scalars().all()

    async def list_by_general_account_id(
        self, general_account_id: UUID
    ) -> Sequence[Note]:
        """List all notes for a general account, including all relationships."""
        stmt = (
            self._get_base_query()
            .join(Note.folder)
            .where(NotebookFolder.general_account_id == general_account_id)
            .order_by(Note.updated_at.desc())
        )
        res = await self.db.execute(stmt)
        return res.unique().scalars().all()

    async def create(self, note_in: NoteCreate) -> Note:
        """Create a new note."""
        db_note = Note(**note_in.model_dump())
        self.db.add(db_note)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status_code=409,
                detail="A note for this trade already exists.",
            )

        await self.db.refresh(db_note)
        # After committing, the note has an ID. We need to fetch it again
        # using our eager-loading method to ensure all relationships are loaded.
        newly_created_note = await self.get_by_id(db_note.id)
        if not newly_created_note:
            raise Exception("Failed to fetch newly created note.")
        return newly_created_note

    async def update(self, db_obj: Note, obj_in: NoteUpdate) -> Note:
        """Update an existing note."""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        self.db.add(db_obj)
        try:
            await self.db.flush()
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status_code=409,
                detail="A note with this trade_id already exists.",
            )

        updated_note = await self.get_by_id(db_obj.id)
        if not updated_note:
            raise Exception("Failed to fetch updated note.")
        return updated_note

    async def delete(self, db_obj: Note) -> None:
        """Delete a note."""
        await self.db.delete(db_obj)
        await self.db.commit()

    async def add_template_to_note(self, note: Note, template: NoteTemplate) -> Note:
        """Associate a note template with a note."""
        note.templates.append(template)
        self.db.add(note)
        await self.db.commit()
        await self.db.refresh(note)
        return note

    async def remove_template_from_note(
        self, note: Note, template: NoteTemplate
    ) -> Note:
        """Disassociate a note template from a note."""
        note.templates.remove(template)
        self.db.add(note)
        await self.db.commit()
        await self.db.refresh(note)
        return note