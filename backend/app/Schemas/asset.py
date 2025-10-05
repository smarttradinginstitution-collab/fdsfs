from __future__ import annotations
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional

class AssetBase(BaseModel):
    symbol: str = Field(min_length=1, max_length=10)
    name: str = Field(min_length=1, max_length=255)
    asset_class_id: UUID


class AssetCreate(AssetBase):
    pass

class AssetUpdate(BaseModel):
    symbol: Optional[str] = Field(default=None, min_length=1, max_length=10)
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    asset_class_id: Optional[UUID] = None
    
class AssetRead(AssetBase):
    id: UUID

    class Config:
        from_attributes = True