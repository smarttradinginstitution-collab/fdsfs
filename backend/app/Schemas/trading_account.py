# app/Schemas/trading_account.py
from __future__ import annotations
from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class TradingAccountRead(BaseModel):
    id: UUID
    general_account_id: UUID
    broker_id: Optional[UUID] = None
    label: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TradingAccountCreate(BaseModel):
    label: Optional[str] = None
    broker_id: Optional[UUID] = None