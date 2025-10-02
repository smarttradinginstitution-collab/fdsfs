from __future__ import annotations
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional

class AssetClassBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)

class AssetClassCreate(AssetClassBase):
    pass

class AssetClassUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)

class AssetClassRead(AssetClassBase):
    id: UUID

    class Config:
        from_attributes = True