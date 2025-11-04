# backend/app/Schemas/platform.py
from __future__ import annotations
from uuid import UUID
from pydantic import BaseModel

class PlatformBase(BaseModel):
    name: str

class PlatformCreate(PlatformBase):
    pass

class PlatformUpdate(PlatformBase):
    pass

class PlatformRead(PlatformBase):
    id: UUID

    model_config = {
        "from_attributes": True,
    }
