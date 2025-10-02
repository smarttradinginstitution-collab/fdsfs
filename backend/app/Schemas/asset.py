from __future__ import annotations
from uuid import UUID
from pydantic import BaseModel, constr, Field
from typing import Optional

class AssetBase(BaseModel):
    symbol: constr(min_length=1, max_length=10)
    name: constr(min_length=1, max_length=255)
    asset_class_id: UUID
    market: Optional[str] = None

class AssetCreate(AssetBase):
    pass

class AssetUpdate(BaseModel):
    symbol: Optional[constr(min_length=1, max_length=10)] = None
    name: Optional[constr(min_length=1, max_length=255)] = None
    asset_class_id: Optional[UUID] = None
    market: Optional[str] = None

class AssetRead(AssetBase):
    id: UUID

    class Config:
        from_attributes = True