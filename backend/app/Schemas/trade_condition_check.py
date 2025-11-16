# app/Schemas/trade_condition_check.py
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class TradeConditionCheckBase(BaseModel):
    was_met: bool
    live_value: Optional[str] = None

class TradeConditionCheckCreate(TradeConditionCheckBase):
    trade_id: UUID
    condition_id: UUID

class TradeConditionCheckRead(TradeConditionCheckBase):
    id: UUID

    class Config:
        orm_mode = True
