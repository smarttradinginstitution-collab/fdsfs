from __future__ import annotations

from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.Models.note_template import NoteTemplate
from app.Schemas.note_template import NoteTemplateCreate, NoteTemplateUpdate


class NoteTemplateRepository:
    """Repository for NoteTemplate CRUD operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, note_template_id: UUID) -> NoteTemplate | None:
        """Get a note template by its ID, including its related notes."""
        stmt = (
            select(NoteTemplate)
            .options(selectinload(NoteTemplate.notes))
            .where(NoteTemplate.id == note_template_id)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().first()

    async def list_by_general_account_id(
        self, general_account_id: UUID
    ) -> Sequence[NoteTemplate]:
        """List all note templates for a given general account."""
        stmt = (
            select(NoteTemplate)
            .where(NoteTemplate.general_account_id == general_account_id)
            .order_by(NoteTemplate.title)
        )
        res = await self.db.execute(stmt)
        return res.unique().scalars().all()

    async def create(self, note_template_in: NoteTemplateCreate) -> NoteTemplate:
        """Create a new note template."""
        db_note_template = NoteTemplate(**note_template_in.model_dump())
        self.db.add(db_note_template)
        await self.db.commit()
        await self.db.refresh(db_note_template)
        return db_note_template

    async def update(
        self, db_obj: NoteTemplate, obj_in: NoteTemplateUpdate
    ) -> NoteTemplate:
        """Update an existing note template."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: NoteTemplate) -> None:
        """Delete a note template."""
        await self.db.delete(db_obj)
        await self.db.commit()