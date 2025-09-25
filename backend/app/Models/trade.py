# app/Models/trade.py
from __future__ import annotations

import enum
import uuid
from typing import Any, Optional, TYPE_CHECKING

from sqlalchemy import (
    Text,
    TIMESTAMP,
    ForeignKey,
    Numeric,
    Float,
    func,
)
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.db import Base

if TYPE_CHECKING:
    from app.Models.trading_account import TradingAccount
    from app.Models.asset import Asset
    from app.Models.tag import Tag
    from app.Models.mistake import Mistake
    from app.Models.playbook import Playbook
    from app.Models.news_impact import NewsImpact
    from app.Models.psychology_state import PsychologyState
    from app.Models.trades_tags import TradesTags
    from app.Models.trades_mistakes import TradesMistakes
    from app.Models.trades_playbooks import TradesPlaybooks
    from app.Models.trades_news_impacts import TradesNewsImpacts
    from app.Models.trades_psychology import TradesPsychology


class TradeDirectionEnum(enum.Enum):
    Long = "Long"
    Short = "Short"


class Trade(Base):
    __tablename__ = "trades"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    trading_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.trading_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    asset_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.assets.id"),
        nullable=True,
    )

    created_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    p_l: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    stop_loss_price: Mapped[Optional[Numeric]] = mapped_column(Numeric, nullable=True)
    take_profit_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    entry_price: Mapped[Optional[Numeric]] = mapped_column(Numeric, nullable=True)
    exit_price: Mapped[Optional[Numeric]] = mapped_column(Numeric, nullable=True)
    position_size: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lowest_price_during_trade: Mapped[Optional[Numeric]] = mapped_column(
        Numeric, nullable=True
    )
    highest_price_during_trade: Mapped[Optional[Numeric]] = mapped_column(
        Numeric, nullable=True
    )
    symbol: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    direction: Mapped[Optional[TradeDirectionEnum]] = mapped_column(
        ENUM(TradeDirectionEnum, name="trade_direction", create_type=False),
        nullable=True,
    )
    notes_pre_trade: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes_post_trade: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    entry_timestamp: Mapped[Optional[Any]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    exit_timestamp: Mapped[Optional[Any]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )

    # Relazioni Principali
    trading_account: Mapped["TradingAccount"] = relationship(
        "TradingAccount", back_populates="trades"
    )
    asset: Mapped[Optional["Asset"]] = relationship("Asset", back_populates="trades")

    # Relazioni Many-to-Many
    tags: Mapped[list["Tag"]] = relationship(
        secondary="public.trades_tags", back_populates="trades"
    )
    tag_links: Mapped[list["TradesTags"]] = relationship(
        "TradesTags",
        back_populates="trade",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    mistakes: Mapped[list["Mistake"]] = relationship(
        "Mistake", secondary="public.trades_mistakes", back_populates="trades"
    )
    mistake_links: Mapped[list["TradesMistakes"]] = relationship(
        "TradesMistakes",
        back_populates="trade",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    playbooks: Mapped[list["Playbook"]] = relationship(
        "Playbook", secondary="public.trades_playbooks", back_populates="trades"
    )
    playbook_links: Mapped[list["TradesPlaybooks"]] = relationship(
        "TradesPlaybooks",
        back_populates="trade",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    news_impacts: Mapped[list["NewsImpact"]] = relationship(
        "NewsImpact", secondary="public.trades_news_impacts", back_populates="trades"
    )
    news_impact_links: Mapped[list["TradesNewsImpacts"]] = relationship(
        "TradesNewsImpacts",
        back_populates="trade",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    psychology_states: Mapped[list["PsychologyState"]] = relationship(
        "PsychologyState", secondary="public.trades_psychology", back_populates="trades"
    )
    psychology_links: Mapped[list["TradesPsychology"]] = relationship(
        "TradesPsychology",
        back_populates="trade",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )