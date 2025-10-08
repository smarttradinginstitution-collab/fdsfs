from __future__ import annotations
from uuid import UUID
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.Infrastructure.db import get_db
from app.Repositories.note_template_repository import NoteTemplateRepository
from app.Repositories.note_repository import NoteRepository
from app.Repositories.general_account_repository import GeneralAccountRepository
from app.Models.note_template import NoteTemplate
from app.Models.note import Note
from app.Schemas.note_template import NoteTemplateCreate, NoteTemplateUpdate

class NoteTemplateService:
    """Service layer for note template operations."""

    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
        self.template_repo = NoteTemplateRepository(db)
        self.note_repo = NoteRepository(db)
        self.general_account_repo = GeneralAccountRepository(db)

    async def _get_general_account_id(self, user_id: UUID) -> UUID:
        """Helper to get the general_account_id for a user."""
        general_account = await self.general_account_repo.get_by_user_id(user_id)
        if not general_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="General account not found for this user.",
            )
        return general_account.id

    async def get_template(self, template_id: UUID, user_id: UUID) -> NoteTemplate:
        """Get a specific template, ensuring it belongs to the user."""
        general_account_id = await self._get_general_account_id(user_id)
        template = await self.template_repo.get_by_id(template_id)
        if not template or template.general_account_id != general_account_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
            )
        return template

    async def get_all_templates(self, user_id: UUID) -> List[NoteTemplate]:
        """Get all templates for the current user."""
        general_account_id = await self._get_general_account_id(user_id)
        return await self.template_repo.list_by_general_account_id(general_account_id)

    async def create_template(self, template_in: NoteTemplateCreate, user_id: UUID) -> NoteTemplate:
        """Create a new template for the user."""
        general_account_id = await self._get_general_account_id(user_id)
        template_in.general_account_id = general_account_id
        return await self.template_repo.create(template_in)

    async def update_template(
        self, template_id: UUID, template_in: NoteTemplateUpdate, user_id: UUID
    ) -> NoteTemplate:
        """Update a template, ensuring it belongs to the user."""
        template = await self.get_template(template_id, user_id)
        return await self.template_repo.update(template, template_in)

    async def delete_template(self, template_id: UUID, user_id: UUID) -> None:
        """Delete a template, ensuring it belongs to the user."""
        template = await self.get_template(template_id, user_id)
        await self.template_repo.delete(template)

    async def add_template_to_note(self, note_id: UUID, template_id: UUID, user_id: UUID) -> Note:
        """Associate a template with a note, ensuring both belong to the user."""
        general_account_id = await self._get_general_account_id(user_id)

        note = await self.note_repo.get_by_id(note_id)
        if not note or note.folder.general_account_id != general_account_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
            )

        template = await self.get_template(template_id, user_id)

        if template in note.templates:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Template already associated with this note.",
            )

        return await self.note_repo.add_template_to_note(note, template)

    async def remove_template_from_note(self, note_id: UUID, template_id: UUID, user_id: UUID) -> Note:
        """Disassociate a template from a note, ensuring both belong to the user."""
        general_account_id = await self._get_general_account_id(user_id)

        note = await self.note_repo.get_by_id(note_id)
        if not note or note.folder.general_account_id != general_account_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
            )

        template = await self.get_template(template_id, user_id)

        if template not in note.templates:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not associated with this note.",
            )

        return await self.note_repo.remove_template_from_note(note, template)