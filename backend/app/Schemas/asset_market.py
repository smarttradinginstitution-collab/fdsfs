from pydantic import BaseModel, ConfigDict
from uuid import UUID
import datetime

# Schema for creating an asset market
class AssetMarketCreate(BaseModel):
    name: str

# Schema for updating an asset market
class AssetMarketUpdate(BaseModel):
    name: str | None = None

# Base schema for reading an asset market, includes all fields
class AssetMarketRead(BaseModel):
    id: UUID
    name: str
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)