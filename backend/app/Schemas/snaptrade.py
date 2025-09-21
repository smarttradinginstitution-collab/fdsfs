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

from app.Schemas.security import SecurityRead

# Schemas for AccountPosition
class AccountPositionBase(BaseModel):
    units: float
    price: Optional[float] = None
    currency: Optional[str] = None
    open_pnl: Optional[float] = None
    average_purchase_price: Optional[float] = None
    cash_equivalent: Optional[bool] = None

class AccountPositionCreate(AccountPositionBase):
    security_id: uuid.UUID

class AccountPositionRead(AccountPositionBase):
    id: uuid.UUID
    security: SecurityRead

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

# Schemas for AccountOrderOption
class AccountOrderOptionBase(BaseModel):
    option_ticker: str
    option_type: Optional[str] = None
    strike_price: Optional[float] = None
    expiration_date: Optional[datetime.date] = None
    is_mini_option: Optional[bool] = None

class AccountOrderOptionCreate(AccountOrderOptionBase):
    underlying_security_id: Optional[uuid.UUID] = None

class AccountOrderOptionRead(AccountOrderOptionBase):
    id: uuid.UUID
    underlying_security_id: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True

# Schemas for AccountOrder
class AccountOrderBase(BaseModel):
    id: str  # brokerage_order_id from SnapTrade
    symbol: str
    action: Optional[str] = None
    status: Optional[str] = None
    total_quantity: Optional[float] = None
    open_quantity: Optional[float] = None
    canceled_quantity: Optional[float] = None
    filled_quantity: Optional[float] = None
    execution_price: Optional[float] = None
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    order_type: Optional[str] = None
    time_in_force: Optional[str] = None
    time_placed: Optional[datetime.datetime] = None
    time_updated: Optional[datetime.datetime] = None
    time_executed: Optional[datetime.datetime] = None
    expiry_date: Optional[datetime.datetime] = None
    take_profit_order_id: Optional[str] = None
    stop_loss_order_id: Optional[str] = None
    quote_universal_symbol: Optional[dict] = None
    quote_currency: Optional[dict] = None

class AccountOrderCreate(AccountOrderBase):
    option_details: Optional[AccountOrderOptionCreate] = None

class AccountOrderRead(AccountOrderBase):
    option_details: Optional[AccountOrderOptionRead] = None
    class Config:
        from_attributes = True

# Schemas for enriched Brokerage Account data in the holdings response
class BrokerageAccountReadForHoldings(BaseModel):
    id: uuid.UUID
    name: Optional[str] = None
    number: Optional[str] = None
    status: Optional[str] = None
    sync_status: Optional[dict] = None

    class Config:
        from_attributes = True

# Final response model for the holdings endpoint
class AccountHoldingsRead(BaseModel):
    account: BrokerageAccountReadForHoldings
    positions: list[AccountPositionRead]
    balances: list[AccountBalanceRead]
    orders: list[AccountOrderRead]
    warning: Optional[dict] = None

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
