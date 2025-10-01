from __future__ import annotations

import uuid
from pydantic import BaseModel


# Schema for creating an association
class BrokerAssetClassCreate(BaseModel):
    asset_class_id: uuid.UUID


# Schema for reading an association
class BrokerAssetClassRead(BaseModel):
    id: uuid.UUID
    broker_id: uuid.UUID
    asset_class_id: uuid.UUID

    class Config:
        orm_mode = True
