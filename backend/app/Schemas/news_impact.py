# app/Schemas/news_impact.py
from __future__ import annotations
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class NewsImpactBase(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = Field(default="#888888", max_length=7)


class NewsImpactCreate(NewsImpactBase):
    pass


class NewsImpactUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = Field(default=None, max_length=7)


class NewsImpactRead(NewsImpactBase):
    id: UUID
    general_account_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)