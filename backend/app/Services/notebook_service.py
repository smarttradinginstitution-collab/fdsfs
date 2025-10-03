# app/Services/notebook_service.py
from __future__ import annotations
from uuid import UUID
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Repositories.notebook_folder_repository import NotebookFolderRepository
from app.Repositories.note_repository import NoteRepository
from app.Repositories.general_account_repository import GeneralAccountRepository
from app.Models.notebook_folder import NotebookFolder
from app.Models.note import Note
from app.Models.enums import FolderType
from app.Schemas.notebook import (
    NotebookFolderCreate,
    NotebookFolderUpdate,
    NoteCreate,
    NoteUpdate,
)

# Define system folders as a constant
SYSTEM_FOLDERS = [
    "Daily Journal",
    "Weekly Notes",
    "Trade Notes",
    "Sessions Recap",
    "Backtesting Session Note Folder",
]

class NotebookService:
    """Service layer for notebook operations."""

    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
        self.folder_repo = NotebookFolderRepository(db)
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

    async def _ensure_system_folders_exist(self, general_account_id: UUID):
        """Checks for and creates missing system folders."""
        for folder_name in SYSTEM_FOLDERS:
            existing_folder = await self.folder_repo.find_by_name_and_account(
                name=folder_name, general_account_id=general_account_id
            )
            if not existing_folder:
                new_folder = NotebookFolder(
                    name=folder_name,
                    general_account_id=general_account_id,
                    folder_type=FolderType.SYSTEM,
                )
                self.db.add(new_folder)
        await self.db.commit()

    # --- Folder Operations ---

    async def get_all_folders(self, user_id: UUID):
        """Get all folders for the current user, ensuring system folders are created."""
        general_account_id = await self._get_general_account_id(user_id)
        await self._ensure_system_folders_exist(general_account_id)
        return await self.folder_repo.list_by_general_account_id(general_account_id)

    async def get_folder(self, folder_id: UUID, user_id: UUID) -> NotebookFolder:
        """Get a specific folder, ensuring it belongs to the user."""
        general_account_id = await self._get_general_account_id(user_id)
        folder = await self.folder_repo.get_by_id(folder_id)
        if not folder or folder.general_account_id != general_account_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found"
            )
        return folder

    async def create_folder(self, folder_in: NotebookFolderCreate, user_id: UUID) -> NotebookFolder:
        """Create a new folder for the user."""
        general_account_id = await self._get_general_account_id(user_id)
        return await self.folder_repo.create(folder_in, general_account_id)

    async def update_folder(
        self, folder_id: UUID, folder_in: NotebookFolderUpdate, user_id: UUID
    ) -> NotebookFolder:
        """Update a folder, ensuring it belongs to the user."""
        folder = await self.get_folder(folder_id, user_id)
        return await self.folder_repo.update(folder, folder_in)

    async def delete_folder(self, folder_id: UUID, user_id: UUID) -> None:
        """Delete a folder, ensuring it belongs to the user."""
        folder = await self.get_folder(folder_id, user_id)
        if folder.folder_type == FolderType.SYSTEM:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="System folders cannot be deleted.",
            )
        await self.folder_repo.delete(folder)

    # --- Note Operations ---

    async def get_note(self, note_id: UUID, user_id: UUID) -> Note:
        """Get a specific note, ensuring it belongs to the user."""
        general_account_id = await self._get_general_account_id(user_id)
        note = await self.note_repo.get_by_id(note_id)
        if not note or note.general_account_id != general_account_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
            )
        return note

    async def create_note(self, note_in: NoteCreate, user_id: UUID) -> Note:
        """Create a new note, ensuring the parent folder belongs to the user."""
        general_account_id = await self._get_general_account_id(user_id)
        await self.get_folder(note_in.folder_id, user_id)
        return await self.note_repo.create(note_in, general_account_id)

    async def update_note(self, note_id: UUID, note_in: NoteUpdate, user_id: UUID) -> Note:
        """Update a note, ensuring it belongs to the user."""
        note = await self.get_note(note_id, user_id)
        return await self.note_repo.update(note, note_in)

    async def delete_note(self, note_id: UUID, user_id: UUID) -> None:
        """Delete a note, ensuring it belongs to the user."""
        note = await self.get_note(note_id, user_id)
        await self.note_repo.delete(note)