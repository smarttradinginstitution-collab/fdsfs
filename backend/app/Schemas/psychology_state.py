# app/Schemas/psychology_state.py

from __future__ import annotations
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, Field


class PsychologyStateBase(BaseModel):
    state: str = Field(...)


class PsychologyStateCreate(PsychologyStateBase):
    pass


class PsychologyStateUpdate(BaseModel):
    state: Optional[str] = Field(default=None)


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