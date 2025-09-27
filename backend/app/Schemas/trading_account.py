# app/Schemas/trading_account.py
from __future__ import annotations
from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


from pydantic import condecimal

# Importa lo schema del broker per l'inclusione
from .broker import BrokerRead

class TradingAccountRead(BaseModel):
    id: UUID
    general_account_id: UUID
    broker_id: Optional[UUID] = None
    label: Optional[str] = None
    created_at: datetime
    initial_balance: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    currency: Optional[str] = None

    # Aggiungi il campo per i dati del broker
    broker: Optional[BrokerRead] = None

    class Config:
        from_attributes = True


class TradingAccountCreate(BaseModel):
    label: str
    broker_id: UUID
    initial_balance: condecimal(max_digits=10, decimal_places=2)
    currency: str