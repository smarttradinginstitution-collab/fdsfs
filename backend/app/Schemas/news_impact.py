# app/Schemas/news_impact.py

from __future__ import annotations
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, Field


class NewsImpactBase(BaseModel):
    name: str = Field(..., max_length=100)
    color: Optional[str] = Field(default="#888888", max_length=7)


class NewsImpactCreate(NewsImpactBase):
    pass


class NewsImpactUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=100)
    color: Optional[str] = Field(default=None, max_length=7)


class NewsImpactRead(NewsImpactBase):
    id: UUID
    general_account_id: UUID

    class Config:
        from_attributes = True