# app/Controllers/notebook_controller.py
from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import Depends, Response, status

from app.Services.notebook_service import NotebookService
from app.Schemas.notebook import (
    NotebookFolderRead,
    NotebookFolderReadWithCount,
    NotebookFolderCreate,
    NotebookFolderUpdate,
    NoteRead,
    NoteReadBasic,
    NoteCreate,
    NoteUpdate,
)
from app.Router.dependencies import get_current_user, CurrentUser

class NotebookController:
    """Controller for all notebook-related operations."""

    def __init__(self):
        pass

    async def list_my_folders(
        self,
        current_user: CurrentUser = Depends(get_current_user),
        service: NotebookService = Depends(),
    ) -> List[NotebookFolderReadWithCount]:
        folders = await service.get_all_folders(user_id=current_user.id)
        # Explicitly cast to the correct schema to avoid loading the `notes` relationship
        return [NotebookFolderReadWithCount.model_validate(f) for f in folders]

    async def create_folder(
        self,
        folder_in: NotebookFolderCreate,
        current_user: CurrentUser = Depends(get_current_user),
        service: NotebookService = Depends(),
    ) -> NotebookFolderReadWithCount:
        folder = await service.create_folder(folder_in=folder_in, user_id=current_user.id)
        return NotebookFolderReadWithCount.model_validate(folder)

    async def update_folder(
        self,
        folder_id: UUID,
        folder_in: NotebookFolderUpdate,
        current_user: CurrentUser = Depends(get_current_user),
        service: NotebookService = Depends(),
    ) -> NotebookFolderReadWithCount:
        folder = await service.update_folder(
            folder_id=folder_id, folder_in=folder_in, user_id=current_user.id
        )
        return NotebookFolderReadWithCount.model_validate(folder)

    async def delete_folder(
        self,
        folder_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        service: NotebookService = Depends(),
    ) -> Response:
        await service.delete_folder(folder_id=folder_id, user_id=current_user.id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    async def list_all_my_notes(
        self,
        current_user: CurrentUser = Depends(get_current_user),
        service: NotebookService = Depends(),
    ) -> List[NoteRead]:
        """Lists all notes for the currently authenticated user."""
        return await service.get_all_notes_for_user(user_id=current_user.id)

    async def list_notes_for_folder(
        self,
        folder_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        service: NotebookService = Depends(),
    ) -> List[NoteRead]:
        return await service.get_notes_for_folder(
            folder_id=folder_id, user_id=current_user.id
        )

    async def create_note(
        self,
        note_in: NoteCreate,
        current_user: CurrentUser = Depends(get_current_user),
        service: NotebookService = Depends(),
    ) -> NoteReadBasic:
        note = await service.create_note(note_in=note_in, user_id=current_user.id)
        return NoteReadBasic.model_validate(note)

    async def get_note(
        self,
        note_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        service: NotebookService = Depends(),
    ) -> NoteRead:
        return await service.get_note(note_id=note_id, user_id=current_user.id)

    async def get_note_by_trade_id(
        self,
        trade_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        service: NotebookService = Depends(),
    ) -> NoteRead:
        return await service.get_note_by_trade_id(
            trade_id=trade_id, user_id=current_user.id
        )

    async def update_note(
        self,
        note_id: UUID,
        note_in: NoteUpdate,
        current_user: CurrentUser = Depends(get_current_user),
        service: NotebookService = Depends(),
    ) -> NoteReadBasic:
        note = await service.update_note(
            note_id=note_id, note_in=note_in, user_id=current_user.id
        )
        return NoteReadBasic.model_validate(note)

    async def delete_note(
        self,
        note_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        service: NotebookService = Depends(),
    ) -> Response:
        await service.delete_note(note_id=note_id, user_id=current_user.id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)