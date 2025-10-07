from __future__ import annotations
import uuid
from datetime import datetime
from pydantic import BaseModel

# --- Base Schema ---
class ImageBase(BaseModel):
    filename: str
    url: str

# --- Create Schema ---
# Used when creating an image record in the service/repository layer.
class ImageCreate(ImageBase):
    file_path: str

# --- Read Schema ---
# Used when returning image data from the API.
class ImageRead(ImageBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True