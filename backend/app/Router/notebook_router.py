# app/Router/notebook_router.py
from __future__ import annotations
from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, status

from app.Controllers.notebook_controller import NotebookController
from app.Schemas.notebook import (
    NotebookFolderRead,
    NotebookFolderCreate,
    NotebookFolderUpdate,
    NoteRead,
    NoteCreate,
    NoteUpdate,
)
from app.Router.dependencies import get_current_user, CurrentUser

# The main router for all /notebook endpoints
router = APIRouter(prefix="/api/v1/notebook", tags=["Notebook"])

# Dependency to get the controller instance
def get_controller(service_dep=Depends()) -> NotebookController:
    return NotebookController(service=service_dep)

# --- Notebook Folders Endpoints ---

@router.get(
    "/folders",
    response_model=List[NotebookFolderRead],
    summary="List all notebook folders for the current user",
)
async def list_my_folders(
    current_user: CurrentUser = Depends(get_current_user),
    controller: NotebookController = Depends(get_controller),
):
    return await controller.list_my_folders(current_user)

@router.post(
    "/folders",
    response_model=NotebookFolderRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new notebook folder",
)
async def create_folder(
    folder_in: NotebookFolderCreate,
    current_user: CurrentUser = Depends(get_current_user),
    controller: NotebookController = Depends(get_controller),
):
    return await controller.create_folder(folder_in, current_user)

@router.put(
    "/folders/{folder_id}",
    response_model=NotebookFolderRead,
    summary="Update a notebook folder",
)
async def update_folder(
    folder_id: UUID,
    folder_in: NotebookFolderUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    controller: NotebookController = Depends(get_controller),
):
    return await controller.update_folder(folder_id, folder_in, current_user)

@router.delete(
    "/folders/{folder_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a notebook folder",
)
async def delete_folder(
    folder_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    controller: NotebookController = Depends(get_controller),
):
    await controller.delete_folder(folder_id, current_user)
    return

# --- Notes Endpoints ---

@router.post(
    "/notes",
    response_model=NoteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new note",
)
async def create_note(
    note_in: NoteCreate,
    current_user: CurrentUser = Depends(get_current_user),
    controller: NotebookController = Depends(get_controller),
):
    return await controller.create_note(note_in, current_user)

@router.get(
    "/notes/{note_id}",
    response_model=NoteRead,
    summary="Get a specific note by ID",
)
async def get_note(
    note_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    controller: NotebookController = Depends(get_controller),
):
    return await controller.get_note(note_id, current_user)

@router.put(
    "/notes/{note_id}",
    response_model=NoteRead,
    summary="Update a note",
)
async def update_note(
    note_id: UUID,
    note_in: NoteUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    controller: NotebookController = Depends(get_controller),
):
    return await controller.update_note(note_id, note_in, current_user)

@router.delete(
    "/notes/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a note",
)
async def delete_note(
    note_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    controller: NotebookController = Depends(get_controller),
):
    await controller.delete_note(note_id, current_user)
    return