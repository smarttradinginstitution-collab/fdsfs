from __future__ import annotations
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal

from .broker import BrokerRead
from .trade import TradeRead


class TradingAccountRead(BaseModel):
    id: UUID
    general_account_id: UUID
    broker_id: Optional[UUID] = None
    label: Optional[str] = None
    created_at: datetime
    initial_balance: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    currency: Optional[str] = None
    broker_name: Optional[str] = Field(None, alias='broker_name')
    broker: Optional[BrokerRead] = None
    trades: List[TradeRead] = []

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TradingAccountCreate(BaseModel):
    label: str
    broker_id: UUID
    initial_balance: Decimal = Field(..., max_digits=10, decimal_places=2)
    currency: str