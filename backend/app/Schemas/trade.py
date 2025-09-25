# app/Schemas/trade.py
from __future__ import annotations

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

# Schemi per le entità relazionate, per usarle in TradeRead
class TagRead(BaseModel):
    id: UUID
    name: str
    color: Optional[str]

    class Config:
        from_attributes = True

class MistakeRead(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True

class PlaybookRead(BaseModel):
    id: UUID
    title: str

    class Config:
        from_attributes = True

class NewsImpactRead(BaseModel):
    id: UUID
    title: str

    class Config:
        from_attributes = True

class PsychologyStateRead(BaseModel):
    id: UUID
    state: str

    class Config:
        from_attributes = True


class TradeBase(BaseModel):
    symbol: Optional[str] = None
    p_l: Optional[float] = None
    setup: Optional[str] = None
    stop_loss_price: Optional[float] = None
    take_profit_price: Optional[float] = None
    notes: Optional[str] = None
    entry_price: Optional[float] = None
    exit_price: Optional[float] = None
    position_size: Optional[float] = None
    lowest_price_during_trade: Optional[float] = None
    highest_price_during_trade: Optional[float] = None
    direction: Optional[str] = None
    emotional_state: Optional[str] = Field(default=None, max_length=50)
    notes_pre_trade: Optional[str] = None
    notes_post_trade: Optional[str] = None
    entry_timestamp: Optional[datetime] = None
    exit_timestamp: Optional[datetime] = None
    asset_id: Optional[UUID] = None


class TradeCreate(TradeBase):
    trading_account_id: UUID
    tag_ids: Optional[List[UUID]] = []
    mistake_ids: Optional[List[UUID]] = []
    playbook_ids: Optional[List[UUID]] = []
    news_impact_ids: Optional[List[UUID]] = []
    psychology_state_ids: Optional[List[UUID]] = []


class TradeUpdate(TradeBase):
    tag_ids: Optional[List[UUID]] = None  # Se presente, sostituisce le associazioni
    mistake_ids: Optional[List[UUID]] = None
    playbook_ids: Optional[List[UUID]] = None
    news_impact_ids: Optional[List[UUID]] = None
    psychology_state_ids: Optional[List[UUID]] = None


class TradeRead(TradeBase):
    id: UUID
    created_at: datetime
    trading_account_id: UUID

    duration_minutes: Optional[float] = None
    r_multiple: Optional[float] = None

    tags: List[TagRead] = []
    mistakes: List[MistakeRead] = []
    playbooks: List[PlaybookRead] = []
    news_impacts: List[NewsImpactRead] = []
    psychology_states: List[PsychologyStateRead] = []

    class Config:
        from_attributes = True


class TradeFilters(BaseModel):
    symbol: Optional[str] = None
    direction: Optional[str] = None
    setups: Optional[List[str]] = None
    days_of_week: Optional[List[int]] = None
    min_size: Optional[float] = None
    max_size: Optional[float] = None
    tag_ids: Optional[List[UUID]] = None
    mistake_ids: Optional[List[UUID]] = None