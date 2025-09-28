# app/Schemas/tag.py

from __future__ import annotations
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, Field


class TagBase(BaseModel):
    name: str = Field(..., max_length=50)
    color: Optional[str] = Field(default="#888888", max_length=7)


class TagCreate(TagBase):
    pass


class TagUpdate(TagBase):
    name: Optional[str] = Field(default=None, max_length=50)
    color: Optional[str] = Field(default=None, max_length=7)


class TagRead(TagBase):
    id: UUID
    general_account_id: UUID

    class Config:
        from_attributes = True


class TagAdminRead(BaseModel):
    general_account_id: UUID
    user_email: str
    tags: List[TagRead]

    class Config:
        from_attributes = True