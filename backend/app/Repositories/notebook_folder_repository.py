# app/Repositories/notebook_folder_repository.py
from __future__ import annotations

from typing import Sequence
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload

from app.Models.note import Note
from app.Models.notebook_folder import NotebookFolder
from app.Schemas.notebook import NotebookFolderCreate, NotebookFolderUpdate


class NotebookFolderRepository:
    """Repository for NotebookFolder CRUD operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ------------------------
    # Helpers per predicate
    # ------------------------
    @staticmethod
    def _not_deleted_folder():
        """Predicate per sfruttare gli indici parziali su notebook_folders (deleted_at IS NULL)."""
        return NotebookFolder.deleted_at.is_(None)

    @staticmethod
    def _not_deleted_note():
        """Predicate per escludere le note soft-deleted dal conteggio."""
        return Note.deleted_at.is_(None)

    # ------------------------
    # Reads
    # ------------------------
    async def get_by_id(self, folder_id: UUID) -> NotebookFolder | None:
        """Get a folder by its ID, with its note count (excluding deleted notes)."""
        stmt = (
            select(NotebookFolder, func.count(Note.id).label("note_count"))
            .options(noload(NotebookFolder.notes))
            .outerjoin(Note, (Note.folder_id == NotebookFolder.id) & (self._not_deleted_note()))
            .where(NotebookFolder.id == folder_id, self._not_deleted_folder())
            .group_by(NotebookFolder.id)
        )
        result = await self.db.execute(stmt)
        res = result.first()
        if res:
            folder, count = res
            folder.note_count = count
            return folder
        return None

    async def find_by_name_and_account(self, name: str, general_account_id: UUID) -> NotebookFolder | None:
        """Find a folder by name for a specific general account (excluding deleted folders)."""
        stmt = select(NotebookFolder).where(
            NotebookFolder.name == name,
            NotebookFolder.general_account_id == general_account_id,
            self._not_deleted_folder()
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def find_system_folders_by_account(
        self, general_account_id: UUID
    ) -> Sequence[NotebookFolder]:
        """Find all system folders for a specific general account."""
        stmt = select(NotebookFolder).where(
            NotebookFolder.general_account_id == general_account_id,
            NotebookFolder.is_system_folder == True,
            self._not_deleted_folder()
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def list_by_general_account_id(
        self, general_account_id: UUID
    ) -> Sequence[NotebookFolder]:
        """List all non-deleted folders for a given general account, with note counts."""
        stmt = (
            select(NotebookFolder, func.count(Note.id).label("note_count"))
            .options(noload(NotebookFolder.notes))
            .outerjoin(Note, (Note.folder_id == NotebookFolder.id) & (self._not_deleted_note()))
            .where(
                NotebookFolder.general_account_id == general_account_id,
                self._not_deleted_folder()
            )
            .group_by(NotebookFolder.id)
            .order_by(NotebookFolder.name.asc())
        )
        res = await self.db.execute(stmt)

        folders_with_counts = []
        for folder, count in res.all():
            folder.note_count = count
            folders_with_counts.append(folder)

        return folders_with_counts

    # ------------------------
    # Mutations
    # ------------------------
    async def create(
        self, folder_in: NotebookFolderCreate, general_account_id: UUID
    ) -> NotebookFolder:
        """Create a new folder."""
        db_folder = NotebookFolder(
            **folder_in.model_dump(), general_account_id=general_account_id
        )
        self.db.add(db_folder)
        await self.db.commit()
        await self.db.refresh(db_folder)
        # Manually set the count for the new folder, which is always 0
        db_folder.note_count = 0
        return db_folder

    async def update(
        self, db_obj: NotebookFolder, obj_in: NotebookFolderUpdate
    ) -> NotebookFolder:
        """Update an existing folder."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        # Manually refresh the note count as it might have changed
        count_stmt = (
            select(func.count(Note.id))
            .where(Note.folder_id == db_obj.id, self._not_deleted_note())
        )
        note_count = await self.db.scalar(count_stmt)
        db_obj.note_count = note_count
        return db_obj

    async def delete(self, db_obj: NotebookFolder) -> None:
        """Delete a folder (hard delete)."""
        await self.db.delete(db_obj)
        await self.db.commit()
