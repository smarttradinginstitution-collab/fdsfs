# app/Controllers/notebook_controller.py
from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import Depends

from app.Services.notebook_service import NotebookService
from app.Schemas.notebook import (
    NotebookFolderRead,
    NotebookFolderCreate,
    NotebookFolderUpdate,
    NoteRead,
    NoteCreate,
    NoteUpdate,
)
from app.Router.dependencies import CurrentUser

class NotebookController:
    """Controller for all notebook-related operations."""

    def __init__(self, service: NotebookService = Depends()):
        self.service = service

    async def list_my_folders(self, current_user: CurrentUser) -> List[NotebookFolderRead]:
        """Lists all notebook folders for the currently authenticated user."""
        # Let FastAPI handle the serialization via the response_model
        return await self.service.get_all_folders(user_id=current_user.id)

    async def create_folder(
        self, folder_in: NotebookFolderCreate, current_user: CurrentUser
    ) -> NotebookFolderRead:
        """Creates a new notebook folder for the current user."""
        # Let FastAPI handle the serialization
        return await self.service.create_folder(folder_in=folder_in, user_id=current_user.id)

    async def update_folder(
        self, folder_id: UUID, folder_in: NotebookFolderUpdate, current_user: CurrentUser
    ) -> NotebookFolderRead:
        """Updates a specific notebook folder by its ID."""
        # Let FastAPI handle the serialization
        return await self.service.update_folder(
            folder_id=folder_id, folder_in=folder_in, user_id=current_user.id
        )

    async def delete_folder(self, folder_id: UUID, current_user: CurrentUser) -> None:
        """Deletes a specific notebook folder by its ID."""
        await self.service.delete_folder(folder_id=folder_id, user_id=current_user.id)
        return

    async def create_note(self, note_in: NoteCreate, current_user: CurrentUser) -> NoteRead:
        """Creates a new note within a specified folder."""
        # Let FastAPI handle the serialization
        return await self.service.create_note(note_in=note_in, user_id=current_user.id)

    async def get_note(self, note_id: UUID, current_user: CurrentUser) -> NoteRead:
        """Retrieves a specific note by its ID."""
        # Let FastAPI handle the serialization
        return await self.service.get_note(note_id=note_id, user_id=current_user.id)

    async def update_note(
        self, note_id: UUID, note_in: NoteUpdate, current_user: CurrentUser
    ) -> NoteRead:
        """Updates a specific note by its ID."""
        # Let FastAPI handle the serialization
        return await self.service.update_note(
            note_id=note_id, note_in=note_in, user_id=current_user.id
        )

    async def delete_note(self, note_id: UUID, current_user: CurrentUser) -> None:
        """Deletes a specific note by its ID."""
        await self.service.delete_note(note_id=note_id, user_id=current_user.id)
        return