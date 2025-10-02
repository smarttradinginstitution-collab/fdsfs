from __future__ import annotations
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional

class AssetAliasBase(BaseModel):
    asset_id: UUID
    alias: str = Field(min_length=1, max_length=255)
    broker_id: Optional[UUID] = None
    platform_id: Optional[UUID] = None
    is_primary: bool = False

class AssetAliasCreate(AssetAliasBase):
    pass

class AssetAliasUpdate(BaseModel):
    alias: Optional[str] = Field(default=None, min_length=1, max_length=255)
    broker_id: Optional[UUID] = None
    platform_id: Optional[UUID] = None
    is_primary: Optional[bool] = None

class AssetAliasRead(AssetAliasBase):
    id: UUID

    class Config:
        from_attributes = True