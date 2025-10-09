# app/Schemas/psychology_state.py

from __future__ import annotations
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, Field


class PsychologyStateBase(BaseModel):
    name: str = Field(..., max_length=100)
    color: Optional[str] = Field(default="#888888", max_length=7)


class PsychologyStateCreate(PsychologyStateBase):
    pass


class PsychologyStateUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=100)
    color: Optional[str] = Field(default=None, max_length=7)


class PsychologyStateRead(PsychologyStateBase):
    id: UUID
    general_account_id: UUID

    class Config:
        from_attributes = True


class PsychologyStateAdminRead(BaseModel):
    general_account_id: UUID
    user_email: str
    psychology_states: List[PsychologyStateRead]

    class Config:
        from_attributes = True