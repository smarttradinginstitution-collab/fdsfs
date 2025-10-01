from __future__ import annotations
from uuid import UUID
from pydantic import BaseModel, constr

class AssetClassBase(BaseModel):
    name: constr(min_length=1, max_length=255)

class AssetClassCreate(AssetClassBase):
    pass

class AssetClassUpdate(AssetClassBase):
    pass

class AssetClassRead(AssetClassBase):
    id: UUID

    class Config:
        orm_mode = True