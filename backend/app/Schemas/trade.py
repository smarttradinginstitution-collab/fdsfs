# app/Schemas/trade.py
from __future__ import annotations

from typing import Optional, List
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from app.Schemas.asset import AssetRead
from app.Schemas.notebook import NoteRead, NoteReadMinimal
from app.Schemas.image import ImageRead
from app.Schemas.platform import PlatformSummary as PlatformRead

# Schemi per le entità relazionate, per usarle in TradeRead
class TagRead(BaseModel):
    id: UUID
    name: str
    color: Optional[str]
    group_id: UUID  # <-- LA CORREZIONE FONDAMENTALE

    model_config = ConfigDict(from_attributes=True)

class MistakeRead(BaseModel):
    id: UUID
    name: str
    color: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class PlaybookRead(BaseModel):
    id: UUID
    title: str

    model_config = ConfigDict(from_attributes=True)

class NewsImpactRead(BaseModel):
    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)

class PsychologyStateRead(BaseModel):
    id: UUID
    name: str
    color: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RulePlaybookRead(BaseModel):
    id: UUID
    rule: str

    model_config = ConfigDict(from_attributes=True)


class TradeBase(BaseModel):
    is_reviewed: Optional[bool] = None
    symbol_snapshot: Optional[str] = None
    p_l: Optional[float] = None
    stop_loss_price: Optional[float] = None
    take_profit_price: Optional[float] = None
    entry_price: Optional[float] = None
    exit_price: Optional[float] = None
    position_size: Optional[float] = None
    lowest_price_during_trade: Optional[float] = None
    highest_price_during_trade: Optional[float] = None
    direction: Optional[str] = None
    entry_timestamp: Optional[datetime] = None
    exit_timestamp: Optional[datetime] = None
    asset_id: Optional[UUID] = None


class TradeCreate(TradeBase):
    trading_account_id: UUID
    tag_ids: Optional[List[UUID]] = Field(default_factory=list)
    mistake_ids: Optional[List[UUID]] = Field(default_factory=list)
    playbook_id: Optional[UUID] = None
    news_impact_ids: Optional[List[UUID]] = Field(default_factory=list)
    psychology_state_ids: Optional[List[UUID]] = Field(default_factory=list)
    rules_followed_ids: Optional[List[UUID]] = Field(default_factory=list)


class TradeUpdate(TradeBase):
    gross_p_l: Optional[float] = None
    commissions: Optional[float] = None
    tag_ids: Optional[List[UUID]] = None  # Se presente, sostituisce le associazioni
    mistake_ids: Optional[List[UUID]] = None
    playbook_id: Optional[UUID] = None
    news_impact_ids: Optional[List[UUID]] = None
    psychology_state_ids: Optional[List[UUID]] = None


class TradeRead(TradeBase):
    id: UUID
    created_at: datetime
    trading_account_id: UUID
    is_linked_to_note: bool = False # Campo per indicare se il trade è già linkato a una nota

    gross_p_l: Optional[float] = None
    fees: Optional[float] = None
    commissions: Optional[float] = None
    duration_minutes: Optional[float] = None
    r_multiple: Optional[float] = None
    net_roi: Optional[float] = None
    trade_risk: Optional[float] = None
    mae_usd: Optional[float] = None
    mfe_usd: Optional[float] = None
    planned_target: Optional[float] = None
    planned_r_multiple: Optional[float] = None

    tags: List[TagRead] = []
    mistakes: List[MistakeRead] = []
    playbook: Optional[PlaybookRead] = None
    news_impacts: List[NewsImpactRead] = []
    psychology_states: List[PsychologyStateRead] = []
    rules_followed: List[RulePlaybookRead] = []

    model_config = ConfigDict(from_attributes=True)


class TradeFilters(BaseModel):
    direction: Optional[str] = None
    playbook_id: Optional[UUID] = None
    days_of_week: Optional[List[int]] = None
    min_size: Optional[float] = None
    max_size: Optional[float] = None
    tag_ids: Optional[List[UUID]] = None
    mistake_ids: Optional[List[UUID]] = None

class TradeReviewUpdate(BaseModel):
    is_reviewed: bool


# Schemi di base per relazioni non complesse
class TradingAccountReadBasic(BaseModel):
    id: UUID
    label: str

    model_config = ConfigDict(from_attributes=True)


class ImportRunReadBasic(BaseModel):
    id: UUID
    file_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TradeWithDataRead(TradeRead):
    # Relazioni one-to-one / many-to-one
    trading_account: Optional[TradingAccountReadBasic] = None
    asset: Optional[AssetRead] = None
    platform: Optional[PlatformRead] = None
    import_run: Optional[ImportRunReadBasic] = None
    playbook: Optional[PlaybookRead] = None # Già presente in TradeRead

    # Relazioni one-to-many / many-to-many
    notes: List[NoteReadMinimal] = []
    images: List[ImageRead] = []
    tags: List[TagRead] = [] # Già presente in TradeRead
    mistakes: List[MistakeRead] = [] # Già presente in TradeRead
    news_impacts: List[NewsImpactRead] = [] # Già presente in TradeRead
    psychology_states: List[PsychologyStateRead] = [] # Già presente in TradeRead
    rules_followed: List[RulePlaybookRead] = [] # Già presente in TradeRead

    model_config = ConfigDict(from_attributes=True)


# Risolve i riferimenti circolari dopo che tutti i modelli sono stati definiti
NoteRead.model_rebuild()