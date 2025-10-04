# app/Controllers/notebook_controller.py
from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import Depends, Response, status

from app.Services.notebook_service import NotebookService
from app.Schemas.notebook import (
    NotebookFolderRead,
    NotebookFolderCreate,
    NotebookFolderUpdate,
    NoteRead,
    NoteCreate,
    NoteUpdate,
    DeletedItemsRead,
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
    ) -> List[NotebookFolderRead]:
        return await service.get_all_folders(user_id=current_user.id)

    async def create_folder(
        self,
        folder_in: NotebookFolderCreate,
        current_user: CurrentUser = Depends(get_current_user),
        service: NotebookService = Depends(),
    ) -> NotebookFolderRead:
        return await service.create_folder(folder_in=folder_in, user_id=current_user.id)

    async def update_folder(
        self,
        folder_id: UUID,
        folder_in: NotebookFolderUpdate,
        current_user: CurrentUser = Depends(get_current_user),
        service: NotebookService = Depends(),
    ) -> NotebookFolderRead:
        return await service.update_folder(
            folder_id=folder_id, folder_in=folder_in, user_id=current_user.id
        )

    async def delete_folder(
        self,
        folder_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        service: NotebookService = Depends(),
    ) -> Response:
        await service.delete_folder(folder_id=folder_id, user_id=current_user.id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    async def create_note(
        self,
        note_in: NoteCreate,
        current_user: CurrentUser = Depends(get_current_user),
        service: NotebookService = Depends(),
    ) -> NoteRead:
        return await service.create_note(note_in=note_in, user_id=current_user.id)

    async def get_note(
        self,
        note_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        service: NotebookService = Depends(),
    ) -> NoteRead:
        return await service.get_note(note_id=note_id, user_id=current_user.id)

    async def update_note(
        self,
        note_id: UUID,
        note_in: NoteUpdate,
        current_user: CurrentUser = Depends(get_current_user),
        service: NotebookService = Depends(),
    ) -> NoteRead:
        return await service.update_note(
            note_id=note_id, note_in=note_in, user_id=current_user.id
        )

    async def delete_note(
        self,
        note_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        service: NotebookService = Depends(),
    ) -> Response:
        await service.delete_note(note_id=note_id, user_id=current_user.id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    # --- Deleted Items Endpoints ---

    async def get_all_deleted_items(
        self,
        current_user: CurrentUser = Depends(get_current_user),
        service: NotebookService = Depends(),
    ) -> DeletedItemsRead:
        return await service.get_all_deleted_items(user_id=current_user.id)

    async def restore_note(
        self,
        note_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        service: NotebookService = Depends(),
    ) -> NoteRead:
        return await service.restore_note(note_id=note_id, user_id=current_user.id)

    async def restore_folder(
        self,
        folder_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        service: NotebookService = Depends(),
    ) -> NotebookFolderRead:
        return await service.restore_folder(folder_id=folder_id, user_id=current_user.id)

    async def permanently_delete_note(
        self,
        note_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        service: NotebookService = Depends(),
    ) -> Response:
        await service.permanently_delete_note(note_id=note_id, user_id=current_user.id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    async def permanently_delete_folder(
        self,
        folder_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        service: NotebookService = Depends(),
    ) -> Response:
        await service.permanently_delete_folder(folder_id=folder_id, user_id=current_user.id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)