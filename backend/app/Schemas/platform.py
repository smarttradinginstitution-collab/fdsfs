# backend/app/Schemas/platform.py
from __future__ import annotations
from uuid import UUID
from pydantic import BaseModel

class PlatformRead(BaseModel):
    id: UUID
    name: str

    model_config = {
        "from_attributes": True,
    }
