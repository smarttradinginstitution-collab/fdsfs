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

# Schemas for AccountPosition
class AccountPositionBase(BaseModel):
    symbol: str
    description: Optional[str] = None
    units: float
    price: Optional[float] = None
    currency: Optional[str] = None
    open_pnl: Optional[float] = None
    average_purchase_price: Optional[float] = None

class AccountPositionCreate(AccountPositionBase):
    pass

class AccountPositionRead(AccountPositionBase):
    id: uuid.UUID

    class Config:
        from_attributes = True

# Schemas for AccountBalance
class AccountBalanceBase(BaseModel):
    currency_code: str
    cash_amount: Optional[float] = None
    buying_power: Optional[float] = None

class AccountBalanceCreate(AccountBalanceBase):
    pass

class AccountBalanceRead(AccountBalanceBase):
    class Config:
        from_attributes = True

# Schemas for AccountOrder
class AccountOrderBase(BaseModel):
    id: str  # brokerage_order_id from SnapTrade
    symbol: str
    action: Optional[str] = None
    status: Optional[str] = None
    total_quantity: Optional[float] = None
    filled_quantity: Optional[float] = None
    execution_price: Optional[float] = None
    limit_price: Optional[float] = None
    time_placed: Optional[datetime.datetime] = None

class AccountOrderCreate(AccountOrderBase):
    pass

class AccountOrderRead(AccountOrderBase):
    class Config:
        from_attributes = True

# Final response model for the holdings endpoint
class AccountHoldingsRead(BaseModel):
    positions: list[AccountPositionRead]
    balances: list[AccountBalanceRead]
    orders: list[AccountOrderRead]

    class Config:
        from_attributes = True

class ReconnectRequest(BaseModel):
    connection_id: str

class BrokerageConnectionRead(BaseModel):
    id: uuid.UUID
    brokerage_name: str
    status: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True
