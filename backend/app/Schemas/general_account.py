# app/Schemas/general_account.py
from __future__ import annotations
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional


class GeneralAccountRead(BaseModel):
    id: UUID
    user_id: UUID
    label: Optional[EmailStr] = None
    created_at: datetime

    class Config:
        from_attributes = True


class GeneralAccountCreate(BaseModel):
    label: EmailStr