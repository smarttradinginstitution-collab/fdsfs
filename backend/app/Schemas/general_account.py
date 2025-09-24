# app/Schemas/general_account.py
from __future__ import annotations
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr


class GeneralAccountRead(BaseModel):
    id: UUID
    user_id: UUID
    label: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class GeneralAccountCreate(BaseModel):
    label: EmailStr