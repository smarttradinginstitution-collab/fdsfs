from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

# --- Base Schema ---
class ImageBase(BaseModel):
    filename: str
    url: str

# --- Create Schema ---
# Used when creating an image record in the service/repository layer.
class ImageCreate(ImageBase):
    file_path: str

# --- Update Schema ---
class ImageUpdate(BaseModel):
    """Schema for updating an image. All fields are optional."""
    filename: Optional[str] = None
    url: Optional[str] = None
    file_path: Optional[str] = None

# --- Read Schema ---
# Used when returning image data from the API.
class ImageRead(ImageBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True