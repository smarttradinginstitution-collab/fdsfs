# app/Schemas/mistake.py

from __future__ import annotations
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, Field


class MistakeBase(BaseModel):
    name: str = Field(..., max_length=100)
    color: Optional[str] = Field(default="#888888", max_length=7)


class MistakeCreate(MistakeBase):
    pass


class MistakeUpdate(MistakeBase):
    name: Optional[str] = Field(default=None, max_length=100)
    color: Optional[str] = Field(default=None, max_length=7)


class MistakeRead(MistakeBase):
    id: UUID
    general_account_id: UUID

    class Config:
        from_attributes = True


class MistakeAdminRead(BaseModel):
    general_account_id: UUID
    user_email: str
    mistakes: List[MistakeRead]

    class Config:
        from_attributes = True