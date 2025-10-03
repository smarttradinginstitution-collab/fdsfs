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

# Instantiate the controller once, as it's stateless
notebook_controller = NotebookController()

# The main router for all /notebook endpoints
router = APIRouter(prefix="/api/v1/notebook", tags=["Notebook"])


# --- Notebook Folders Endpoints ---

router.get(
    "/folders",
    response_model=List[NotebookFolderRead],
    summary="List all notebook folders for the current user",
)(notebook_controller.list_my_folders)

router.post(
    "/folders",
    response_model=NotebookFolderRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new notebook folder",
)(notebook_controller.create_folder)

router.put(
    "/folders/{folder_id}",
    response_model=NotebookFolderRead,
    summary="Update a notebook folder",
)(notebook_controller.update_folder)

router.delete(
    "/folders/{folder_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a notebook folder",
)(notebook_controller.delete_folder)


# --- Notes Endpoints ---

router.post(
    "/notes",
    response_model=NoteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new note",
)(notebook_controller.create_note)

router.get(
    "/notes/{note_id}",
    response_model=NoteRead,
    summary="Get a specific note by ID",
)(notebook_controller.get_note)

router.put(
    "/notes/{note_id}",
    response_model=NoteRead,
    summary="Update a note",
)(notebook_controller.update_note)

router.delete(
    "/notes/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a note",
)(notebook_controller.delete_note)