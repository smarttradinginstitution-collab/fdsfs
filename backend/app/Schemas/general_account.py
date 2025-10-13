# app/Schemas/general_account.py
from __future__ import annotations
import uuid
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.Schemas.mistake import MistakeRead
from app.Schemas.psychology_state import PsychologyStateRead
from app.Schemas.tags_group import TagsGroupRead
from app.Schemas.playbook import PlaybookRead
from app.Schemas.news_impacts_group import NewsImpactsGroupRead


class GeneralAccountBase(BaseModel):
    label: str


class GeneralAccountCreate(GeneralAccountBase):
    pass


class GeneralAccountUpdate(GeneralAccountBase):
    pass


class GeneralAccountRead(GeneralAccountBase):
    id: uuid.UUID
    user_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class GeneralAccountWithDataRead(GeneralAccountRead):
    mistakes: List[MistakeRead] = []
    news_impacts_groups: List[NewsImpactsGroupRead] = []
    psychology_states: List[PsychologyStateRead] = []
    tags_groups: List[TagsGroupRead] = []
    playbooks: List[PlaybookRead] = []
