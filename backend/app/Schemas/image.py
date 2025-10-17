from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

# --- Base Schema ---
class ImageBase(BaseModel):
    url: str
    filename: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    phase: Optional[str] = None
    is_primary_before: Optional[bool] = Field(default=False)
    is_primary_after: Optional[bool] = Field(default=False)

# --- Create Schema ---
# Used when creating an image record in the service/repository layer.
class ImageCreate(ImageBase):
    general_account_id: uuid.UUID
    trade_id: Optional[uuid.UUID] = None
    storage_path: str

# --- Update Schema ---
class ImageUpdate(BaseModel):
    """Schema for updating an image's metadata. All fields are optional."""
    description: Optional[str] = None
    category: Optional[str] = None
    phase: Optional[str] = None
    is_primary_before: Optional[bool] = None
    is_primary_after: Optional[bool] = None

# --- Read Schema ---
# Used when returning image data from the API.
class ImageRead(ImageBase):
    id: uuid.UUID
    trade_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}