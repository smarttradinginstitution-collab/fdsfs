# app/Schemas/trading_account.py
from __future__ import annotations
from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


from pydantic import condecimal

class TradingAccountRead(BaseModel):
    id: UUID
    general_account_id: UUID
    broker_id: Optional[UUID] = None
    label: Optional[str] = None
    created_at: datetime
    initial_balance: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    currency: Optional[str] = None

    class Config:
        from_attributes = True


class TradingAccountCreate(BaseModel):
    label: str
    broker_id: UUID
    initial_balance: condecimal(max_digits=10, decimal_places=2)
    currency: str