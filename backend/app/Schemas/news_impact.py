# app/Schemas/news_impact.py
from __future__ import annotations
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional


class NewsImpactBase(BaseModel):
    name: Optional[str] = None


class NewsImpactCreate(NewsImpactBase):
    pass


class NewsImpactUpdate(NewsImpactBase):
    pass


class NewsImpactRead(NewsImpactBase):
    id: UUID
    general_account_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)