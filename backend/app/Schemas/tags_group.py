# app/Schemas/tags_group.py
from __future__ import annotations
import uuid
from typing import Optional, List
from pydantic import BaseModel, Field, constr
from app.Schemas.tag import TagRead


class TagsGroupBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    color: Optional[constr(max_length=7)] = "#888888"
    position: Optional[int] = None


class TagsGroupCreate(TagsGroupBase):
    pass


class TagsGroupUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    color: Optional[constr(max_length=7)] = None
    position: Optional[int] = None


class TagsGroupInDB(TagsGroupBase):
    id: uuid.UUID
    general_account_id: uuid.UUID

    class Config:
        from_attributes = True


class TagsGroupRead(TagsGroupInDB):
    tags: List[TagRead] = []


class TagsGroupReorder(BaseModel):
    group_ids: List[uuid.UUID]