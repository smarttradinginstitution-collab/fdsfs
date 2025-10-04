# app/Repositories/notebook_folder_repository.py
from __future__ import annotations

from typing import Sequence
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload

from app.Models.note import Note
from app.Models.notebook_folder import NotebookFolder
from app.Models.enums import FolderType
from app.Schemas.notebook import NotebookFolderCreate, NotebookFolderUpdate


class NotebookFolderRepository:
    """Repository for NotebookFolder CRUD operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, folder_id: UUID) -> NotebookFolder | None:
        """Get a folder by its ID, with its note count."""
        stmt = (
            select(NotebookFolder, func.count(Note.id).label("note_count"))
            .options(noload(NotebookFolder.notes))
            .outerjoin(Note, Note.folder_id == NotebookFolder.id)
            .where(NotebookFolder.id == folder_id)
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
        """Find a folder by name for a specific general account."""
        stmt = select(NotebookFolder).where(
            NotebookFolder.name == name,
            NotebookFolder.general_account_id == general_account_id
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_by_general_account_id(
        self, general_account_id: UUID
    ) -> Sequence[NotebookFolder]:
        """List all folders for a given general account, with note counts."""
        stmt = (
            select(NotebookFolder, func.count(Note.id).label("note_count"))
            .options(noload(NotebookFolder.notes))
            .outerjoin(Note, Note.folder_id == NotebookFolder.id)
            .where(NotebookFolder.general_account_id == general_account_id)
            .group_by(NotebookFolder.id)
            .order_by(NotebookFolder.name.asc())
        )
        res = await self.db.execute(stmt)

        folders_with_counts = []
        for folder, count in res.all():
            folder.note_count = count
            folders_with_counts.append(folder)

        return folders_with_counts


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
        return await self.get_by_id(db_folder.id)

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
        return await self.get_by_id(db_obj.id)

    async def delete(self, db_obj: NotebookFolder) -> None:
        """Delete a folder."""
        await self.db.delete(db_obj)
        await self.db.commit()