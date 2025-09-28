# app/Schemas/playbook.py

from __future__ import annotations
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, Field


class PlaybookBase(BaseModel):
    name: str = Field(..., max_length=50)
    color: Optional[str] = Field(default="#888888", max_length=7)


class PlaybookCreate(PlaybookBase):
    pass


class PlaybookUpdate(PlaybookBase):
    name: Optional[str] = Field(default=None, max_length=50)
    color: Optional[str] = Field(default=None, max_length=7)


class PlaybookRead(PlaybookBase):
    id: UUID
    general_account_id: UUID

    class Config:
        from_attributes = True


class PlaybookAdminRead(BaseModel):
    general_account_id: UUID
    user_email: str
    playbooks: List[PlaybookRead]

    class Config:
        from_attributes = True