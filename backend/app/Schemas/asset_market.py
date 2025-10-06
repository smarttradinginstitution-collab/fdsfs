import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# Base schema for AssetMarket
class AssetMarketBase(BaseModel):
    name: str = Field(..., description="The name of the asset market.")
    code: Optional[str] = Field(None, description="The unique code for the asset market.")


# Schema for creating an AssetMarket
class AssetMarketCreate(AssetMarketBase):
    pass


# Schema for updating an AssetMarket
class AssetMarketUpdate(AssetMarketBase):
    name: Optional[str] = Field(None, description="The name of the asset market.")
    code: Optional[str] = Field(None, description="The unique code for the asset market.")


# Schema for reading an AssetMarket (API response)
class AssetMarketRead(AssetMarketBase):
    id: uuid.UUID = Field(..., description="The unique identifier of the asset market.")
    created_at: datetime = Field(..., description="The timestamp when the asset market was created.")

    class Config:
        from_attributes = True