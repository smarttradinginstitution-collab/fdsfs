# app/Schemas/platform.py
from __future__ import annotations

import uuid
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from app.Schemas.broker import BrokerRead


# Shared properties
class PlatformBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


# Properties to receive on item creation
class PlatformCreate(PlatformBase):
    brokers: list[uuid.UUID] | None = []


# Properties to receive on item update
class PlatformUpdate(PlatformBase):
    brokers: list[uuid.UUID] | None = None


# Properties shared by models stored in DB
class PlatformInDBBase(PlatformBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Properties to return to client
class Platform(PlatformInDBBase):
    pass


# Properties to return to client with broker details
class PlatformSummary(PlatformInDBBase):
    brokers: List[BrokerRead] = []


# Properties stored in DB
class PlatformInDB(PlatformInDBBase):
    pass