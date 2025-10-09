# app/Schemas/general_account.py
from __future__ import annotations
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List

from app.Schemas.mistake import MistakeRead
from app.Schemas.news_impact import NewsImpactRead
from app.Schemas.psychology_state import PsychologyStateRead
from app.Schemas.tags_group import TagsGroupRead


class GeneralAccountRead(BaseModel):
    id: UUID
    user_id: UUID
    label: Optional[EmailStr] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GeneralAccountCreate(BaseModel):
    label: EmailStr


class GeneralAccountWithData(GeneralAccountRead):
    mistakes: List[MistakeRead] = []
    news_impacts: List[NewsImpactRead] = []
    psychology_states: List[PsychologyStateRead] = []
    tags_groups: List[TagsGroupRead] = []

    model_config = ConfigDict(from_attributes=True)