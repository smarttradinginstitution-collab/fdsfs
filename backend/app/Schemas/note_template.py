from __future__ import annotations

import uuid
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

# Forward-declaration for NoteRead
class NoteRead(BaseModel):
    id: uuid.UUID
    title: str

    model_config = ConfigDict(from_attributes=True)

class NoteTemplateBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    text: Optional[str] = None
    url_image: Optional[str] = None

class NoteTemplateCreate(NoteTemplateBase):
    general_account_id: uuid.UUID

class NoteTemplateUpdate(NoteTemplateBase):
    title: Optional[str] = Field(None, min_length=1, max_length=255)

class NoteTemplateRead(NoteTemplateBase):
    id: uuid.UUID
    general_account_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class NoteTemplateReadWithDetails(NoteTemplateRead):
    notes: List[NoteRead] = []

    model_config = ConfigDict(from_attributes=True)