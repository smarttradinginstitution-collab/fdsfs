# app/Schemas/tag.py

from __future__ import annotations
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, Field


class TagBase(BaseModel):
    name: str = Field(..., max_length=50)
    color: Optional[str] = Field(default="#888888", max_length=7)


class TagCreate(TagBase):
    group_id: UUID


class TagUpdate(TagBase):
    name: Optional[str] = Field(default=None, max_length=50)
    color: Optional[str] = Field(default=None, max_length=7)


class TagRead(TagBase):
    id: UUID
    group_id: UUID

    class Config:
        from_attributes = True