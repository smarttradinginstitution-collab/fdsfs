# app/Schemas/notebook.py
from __future__ import annotations
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field
from app.Models.enums import FolderType

# --- Note Schemas ---

class NoteBase(BaseModel):
    title: Optional[str] = Field(None, description="The title of the note")
    content: Optional[Dict[str, Any]] = Field(None, description="The content of the note in JSON format from Tiptap")

    class Config:
        from_attributes = True

class NoteCreate(NoteBase):
    folder_id: UUID = Field(..., description="The ID of the folder this note belongs to")
    title: str = Field(..., description="The title of the note is required for creation")

class NoteUpdate(NoteBase):
    pass

class NoteRead(NoteBase):
    id: UUID
    folder_id: UUID
    trade_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    title: str


# --- NotebookFolder Schemas ---

class NotebookFolderBase(BaseModel):
    name: Optional[str] = Field(None, description="The name of the folder")
    template_content: Optional[Dict[str, Any]] = Field(None, description="The template content for notes in this folder")

    class Config:
        from_attributes = True

class NotebookFolderCreate(NotebookFolderBase):
    name: str = Field(..., description="The name of the folder is required for creation")

class NotebookFolderUpdate(NotebookFolderBase):
    pass

class NotebookFolderRead(NotebookFolderBase):
    id: UUID
    general_account_id: UUID
    folder_type: FolderType
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    name: str
    notes: List[NoteRead] = []
    template_content: Optional[Dict[str, Any]] = None


# --- Schemas for Deleted Items ---

class DeletedNoteInfo(BaseModel):
    id: UUID
    title: str
    deleted_at: Optional[datetime]

    class Config:
        from_attributes = True


class DeletedFolderInfo(BaseModel):
    id: UUID
    name: str
    deleted_at: Optional[datetime]

    class Config:
        from_attributes = True


class DeletedItemsRead(BaseModel):
    deleted_folders: List[DeletedFolderInfo]
    deleted_notes: List[DeletedNoteInfo]