# app/Schemas/news_impacts_group.py
from __future__ import annotations
import uuid
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.Schemas.news_impact import NewsImpactRead


class NewsImpactsGroupBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    color: Optional[str] = Field(default="#888888", max_length=7)
    position: Optional[int] = None


class NewsImpactsGroupCreate(NewsImpactsGroupBase):
    pass


class NewsImpactsGroupUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    color: Optional[str] = Field(default=None, max_length=7)
    position: Optional[int] = None


class NewsImpactsGroupInDB(NewsImpactsGroupBase):
    id: uuid.UUID
    general_account_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class NewsImpactsGroupRead(NewsImpactsGroupInDB):
    news_impacts: List[NewsImpactRead] = []


class NewsImpactsGroupReorder(BaseModel):
    group_ids: List[uuid.UUID]
