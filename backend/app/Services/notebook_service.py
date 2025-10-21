# app/Services/notebook_service.py
from __future__ import annotations
import time
from uuid import UUID
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.Infrastructure.db import get_db
from app.Repositories.notebook_folder_repository import NotebookFolderRepository
from app.Repositories.note_repository import NoteRepository
from app.Repositories.general_account_repository import GeneralAccountRepository
from app.Models.notebook_folder import NotebookFolder
from app.Models.note import Note
from app.Models.enums import FolderType, SystemFolderIdentifier
from app.Schemas.notebook import (
    NotebookFolderCreate,
    NotebookFolderUpdate,
    NoteCreate,
    NoteUpdate,
)

# Define system folders with their specific identifiers
SYSTEM_FOLDERS = {
    "Trade Notes": SystemFolderIdentifier.TRADE_NOTES,
    "Daily Journal": SystemFolderIdentifier.DAILY_JOURNAL,
    "Session Recap": SystemFolderIdentifier.SESSION_RECAP,
}


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
        """
        Checks for and creates missing system folders in a single efficient operation.
        """
        # Get all system folder identifiers that should exist
        required_identifiers = set(SYSTEM_FOLDERS.values())

        # Fetch all system folders that already exist for this account in one query
        existing_folders = await self.folder_repo.find_system_folders_by_account(
            general_account_id
        )
        existing_identifiers = {
            folder.system_folder_identifier for folder in existing_folders
        }

        # Determine which folders are missing
        missing_identifiers = required_identifiers - existing_identifiers

        # If any are missing, create them
        if missing_identifiers:
            folders_to_create = []
            # Create a reverse mapping from identifier to name
            identifier_to_name = {v: k for k, v in SYSTEM_FOLDERS.items()}

            for identifier in missing_identifiers:
                folder_name = identifier_to_name[identifier]
                folders_to_create.append(
                    NotebookFolder(
                        name=folder_name,
                        general_account_id=general_account_id,
                        folder_type=FolderType.SYSTEM,
                        is_system_folder=True,
                        system_folder_identifier=identifier,
                    )
                )

            self.db.add_all(folders_to_create)
            await self.db.commit()

    # --- Folder Operations ---

    async def get_all_folders(self, user_id: UUID):
        """Get all folders for the current user, ensuring system folders are created."""
        start_time = time.time()
        print(f"NOTEBOOK_TIMING: START get_all_folders service")
        general_account_id = await self._get_general_account_id(user_id)
        await self._ensure_system_folders_exist(general_account_id)
        result = await self.folder_repo.list_by_general_account_id(general_account_id)
        end_time = time.time()
        print(f"NOTEBOOK_TIMING: END get_all_folders service. Duration: {end_time - start_time:.4f}s")
        return result

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
        start_time = time.time()
        print(f"NOTEBOOK_TIMING: START create_folder service")
        general_account_id = await self._get_general_account_id(user_id)
        # Check for uniqueness
        existing_folder = await self.folder_repo.find_by_name_and_account(
            name=folder_in.name, general_account_id=general_account_id
        )
        if existing_folder:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A folder with the name '{folder_in.name}' already exists.",
            )
        result = await self.folder_repo.create(folder_in, general_account_id)
        end_time = time.time()
        print(f"NOTEBOOK_TIMING: END create_folder service. Duration: {end_time - start_time:.4f}s")
        return result

    async def update_folder(
        self, folder_id: UUID, folder_in: NotebookFolderUpdate, user_id: UUID
    ) -> NotebookFolder:
        """Update a folder, ensuring it belongs to the user."""
        start_time = time.time()
        print(f"NOTEBOOK_TIMING: START update_folder service")
        folder = await self.get_folder(folder_id, user_id)
        result = await self.folder_repo.update(folder, folder_in)
        end_time = time.time()
        print(f"NOTEBOOK_TIMING: END update_folder service. Duration: {end_time - start_time:.4f}s")
        return result

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

    async def get_all_notes_for_user(self, user_id: UUID) -> List[Note]:
        """Get all notes for the current user's general account."""
        general_account_id = await self._get_general_account_id(user_id)
        return await self.note_repo.list_by_general_account_id(general_account_id)

    async def get_notes_for_folder(self, folder_id: UUID, user_id: UUID) -> List[Note]:
        """Get all notes for a specific folder, ensuring it belongs to the user."""
        # First, verify the user has access to this folder.
        await self.get_folder(folder_id, user_id)
        # Then, fetch the notes.
        return await self.note_repo.list_by_folder_id(folder_id)

    async def get_note(self, note_id: UUID, user_id: UUID) -> Note:
        """Get a specific note, ensuring it belongs to the user."""
        start_time = time.time()
        print(f"NOTEBOOK_TIMING: START get_note service")
        general_account_id = await self._get_general_account_id(user_id)
        note = await self.note_repo.get_by_id(note_id)
        # The folder is eager-loaded by the repository's get_by_id method
        if not note or not note.folder or note.folder.general_account_id != general_account_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
            )
        end_time = time.time()
        print(f"NOTEBOOK_TIMING: END get_note service. Duration: {end_time - start_time:.4f}s")
        return note

    async def get_note_by_trade_id(self, trade_id: UUID, user_id: UUID) -> Note:
        """Get a note by its linked trade_id, ensuring it belongs to the user."""
        general_account_id = await self._get_general_account_id(user_id)
        note = await self.note_repo.get_by_trade_id(
            trade_id=trade_id, general_account_id=general_account_id
        )

        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note for the specified trade not found.",
            )
        return note

    async def create_note(self, note_in: NoteCreate, user_id: UUID) -> Note:
        """Create a new note, ensuring the parent folder belongs to the user."""
        # The `get_folder` call ensures that the folder belongs to the user,
        # which implicitly confirms ownership.
        await self.get_folder(note_in.folder_id, user_id)

        # Check for uniqueness of trade_id
        if note_in.trade_id:
            general_account_id = await self._get_general_account_id(user_id)
            existing_note = await self.note_repo.get_by_trade_id(
                trade_id=note_in.trade_id, general_account_id=general_account_id
            )
            if existing_note:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"A note for trade '{note_in.trade_id}' already exists.",
                )

        return await self.note_repo.create(note_in)

    async def update_note(self, note_id: UUID, note_in: NoteUpdate, user_id: UUID) -> Note:
        """Update a note, ensuring it belongs to the user."""
        start_time = time.time()
        print(f"NOTEBOOK_TIMING: START update_note service")
        note = await self.get_note(note_id, user_id)
        result = await self.note_repo.update(note, note_in)
        end_time = time.time()
        print(f"NOTEBOOK_TIMING: END update_note service. Duration: {end_time - start_time:.4f}s")
        return result

    async def delete_note(self, note_id: UUID, user_id: UUID) -> None:
        """Delete a note, ensuring it belongs to the user."""
        note = await self.get_note(note_id, user_id)
        await self.note_repo.delete(note)