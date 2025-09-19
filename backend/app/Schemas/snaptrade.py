# app/Schemas/snaptrade.py
from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
import uuid
import datetime

class ProfileRead(BaseModel):
    # We only expose whether the secret exists, not the secret itself, for security.
    has_snaptrade_user_secret: bool = False

    class Config:
        from_attributes = True

class BrokerageConnectionRead(BaseModel):
    id: uuid.UUID
    brokerage_name: str
    status: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True
