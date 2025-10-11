# app/Services/notebook_service.py
from __future__ import annotations
from uuid import UUID
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import date

from app.Infrastructure.db import get_db
from app.Repositories.notebook_folder_repository import NotebookFolderRepository
from app.Repositories.note_repository import NoteRepository
from app.Repositories.general_account_repository import GeneralAccountRepository
from app.Repositories.trade_repository import TradeRepository
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
        self.trade_repo = TradeRepository(db)

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
        for folder_name, identifier in SYSTEM_FOLDERS.items():
            existing_folder = await self.folder_repo.find_by_name_and_account(
                name=folder_name, general_account_id=general_account_id
            )
            if not existing_folder:
                new_folder = NotebookFolder(
                    name=folder_name,
                    general_account_id=general_account_id,
                    folder_type=FolderType.SYSTEM,
                    is_system_folder=True,
                    system_folder_identifier=identifier,
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
        # Check for uniqueness
        existing_folder = await self.folder_repo.find_by_name_and_account(
            name=folder_in.name, general_account_id=general_account_id
        )
        if existing_folder:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A folder with the name '{folder_in.name}' already exists.",
            )
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
        general_account_id = await self._get_general_account_id(user_id)
        note = await self.note_repo.get_by_id(note_id)
        # The folder is eager-loaded by the repository's get_by_id method
        if not note or not note.folder or note.folder.general_account_id != general_account_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
            )
        return note

    async def create_note(self, note_in: NoteCreate, user_id: UUID) -> Note:
        """Create a new note, ensuring the parent folder belongs to the user."""
        # The `get_folder` call ensures that the folder belongs to the user,
        # which implicitly confirms ownership.
        await self.get_folder(note_in.folder_id, user_id)

        # Check for uniqueness of trade_id
        if note_in.trade_id:
            existing_note = await self.note_repo.get_by_trade_id(note_in.trade_id)
            if existing_note:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"A note for trade '{note_in.trade_id}' already exists.",
                )

        return await self.note_repo.create(note_in)

    async def update_note(self, note_id: UUID, note_in: NoteUpdate, user_id: UUID) -> Note:
        """Update a note, ensuring it belongs to the user."""
        note = await self.get_note(note_id, user_id)
        return await self.note_repo.update(note, note_in)

    async def delete_note(self, note_id: UUID, user_id: UUID) -> None:
        """Delete a note, ensuring it belongs to the user."""
        note = await self.get_note(note_id, user_id)
        await self.note_repo.delete(note)

    # --- Get-or-Create Operations ---

    async def get_or_create_trade_note(self, trade_id: UUID, user_id: UUID) -> Note:
        """
        Retrieves the note for a specific trade. If it doesn't exist,
        it creates one in the 'Trade Notes' system folder.
        """
        general_account_id = await self._get_general_account_id(user_id)

        # 1. Verify the trade exists and belongs to the user
        trade = await self.trade_repo.get_by_id_and_general_account_id(
            trade_id, general_account_id
        )
        if not trade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Trade not found"
            )

        # 2. Check if a note for this trade already exists
        existing_note = await self.note_repo.get_by_trade_id(trade_id)
        if existing_note:
            return existing_note

        # 3. Ensure 'Trade Notes' system folder exists and get it
        await self._ensure_system_folders_exist(general_account_id)
        trade_notes_folder = await self.folder_repo.find_by_system_identifier(
            SystemFolderIdentifier.TRADE_NOTES, general_account_id
        )
        if not trade_notes_folder:
            # This should theoretically not happen due to _ensure_system_folders_exist
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Trade Notes system folder not found.",
            )

        # 4. Create the new note
        note_title = f"{trade.symbol_snapshot} - {trade.entry_timestamp.strftime('%Y-%m-%d')}"
        note_in = NoteCreate(
            title=note_title,
            content={"type": "doc", "content": [{"type": "paragraph"}]},
            folder_id=trade_notes_folder.id,
            trade_id=trade_id,
        )
        return await self.note_repo.create(note_in)


    async def get_or_create_daily_journal_note(self, journal_date: date, user_id: UUID) -> Note:
        """
        Retrieves the journal note for a specific day. If it doesn't exist,
        it creates one in the 'Daily Journal' system folder.
        """
        general_account_id = await self._get_general_account_id(user_id)

        # 1. Format the title consistently
        note_title = f"Journal - {journal_date.strftime('%Y-%m-%d')}"

        # 2. Check if a note for this day already exists in the correct folder
        existing_note = await self.note_repo.find_by_title_and_account(
            note_title, general_account_id
        )
        if existing_note and existing_note.folder.system_folder_identifier == SystemFolderIdentifier.DAILY_JOURNAL:
            return existing_note

        # 3. Ensure 'Daily Journal' system folder exists and get it
        await self._ensure_system_folders_exist(general_account_id)
        daily_journal_folder = await self.folder_repo.find_by_system_identifier(
            SystemFolderIdentifier.DAILY_JOURNAL, general_account_id
        )
        if not daily_journal_folder:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Daily Journal system folder not found.",
            )

        # 4. If a note with that title exists but in a different folder, it's a conflict.
        # This is a rare edge case, but good to handle.
        if existing_note:
             raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A note with the title '{note_title}' already exists but is not in the Daily Journal folder.",
            )

        # 5. Create the new note
        note_in = NoteCreate(
            title=note_title,
            content={"type": "doc", "content": [{"type": "paragraph"}]},
            folder_id=daily_journal_folder.id,
        )
        return await self.note_repo.create(note_in)