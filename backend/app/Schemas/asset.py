from __future__ import annotations
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from .asset_market import AssetMarketRead
from .asset_class import AssetClassRead

class AssetBase(BaseModel):
    symbol: str = Field(min_length=1, max_length=10)
    name: str = Field(min_length=1, max_length=255)
    asset_class_id: UUID
    asset_market_id: UUID

class AssetCreate(AssetBase):
    pass

class AssetUpdate(BaseModel):
    symbol: Optional[str] = Field(default=None, min_length=1, max_length=10)
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    asset_class_id: Optional[UUID] = None
    asset_market_id: Optional[UUID] = None

class AssetRead(AssetBase):
    id: UUID
    asset_class: AssetClassRead
    asset_market: AssetMarketRead

    model_config = ConfigDict(from_attributes=True)