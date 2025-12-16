# app/Models/trade.py
from __future__ import annotations

import uuid
from typing import Any, Optional, TYPE_CHECKING, List

from sqlalchemy import (
    Text,
    TIMESTAMP,
    ForeignKey,
    Numeric,
    Float,
    func,
    String,
    Enum,
    Boolean,
    text,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.db import Base
from app.Models.enums import TradeDirection, TradeStatus  # Use centralized ENUMs

from app.Models.rule_playbook import trades_rules_association

if TYPE_CHECKING:
    from app.Models.trading_account import TradingAccount
    from app.Models.asset import Asset
    from app.Models.platform import Platform
    from app.Models.import_run import ImportRun
    from app.Models.tag import Tag
    from app.Models.note import Note
    from app.Models.image import Image
    from app.Models.mistake import Mistake
    from app.Models.playbook import Playbook
    from app.Models.news_impact import NewsImpact
    from app.Models.psychology_state import PsychologyState
    from app.Models.rule_playbook import RulePlaybook


class Trade(Base):
    __tablename__ = "trades"
    __table_args__ = (
        Index('uq_trades_account_dedupe', 'trading_account_id', 'dedupe_key', unique=True, postgresql_where=text('dedupe_key IS NOT NULL')),
        Index('idx_trades_parent_trade_id', 'parent_trade_id'),
        {"schema": "public"}
    )

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
        ForeignKey("public.assets.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    platform_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.platforms.id"),
        nullable=True,
        index=True,
    )
    import_run_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.import_runs.id"),
        nullable=True,
        index=True,
    )
    playbook_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.playbooks.id"),
        nullable=True,
        index=True
    )

    # Parent Trade Relationship
    parent_trade_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.trades.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Core trade data
    gross_p_l: Mapped[Optional[Numeric]] = mapped_column(Numeric, nullable=True)
    p_l: Mapped[Optional[Numeric]] = mapped_column(Numeric, nullable=True) # Questo è il P&L Netto
    r_multiple: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    entry_price: Mapped[Optional[Numeric]] = mapped_column(Numeric, nullable=True)
    exit_price: Mapped[Optional[Numeric]] = mapped_column(Numeric, nullable=True)
    position_size: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    entry_timestamp: Mapped[Optional[Any]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    exit_timestamp: Mapped[Optional[Any]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    direction: Mapped[Optional[TradeDirection]] = mapped_column(
        Enum(TradeDirection, name="direction", schema="public"),
        nullable=True,
    )
    status: Mapped[TradeStatus] = mapped_column(
        Enum(TradeStatus, name="trade_status", schema="public"),
        nullable=False,
        default=TradeStatus.closed,
        index=True,
    )
    is_reviewed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )

    # Financial details
    fees: Mapped[Optional[Numeric]] = mapped_column(Numeric, nullable=True, default=0)
    commissions: Mapped[Optional[Numeric]] = mapped_column(Numeric, nullable=True, default=0)
    currency: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)

    # Import-related fields
    external_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    dedupe_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    symbol_snapshot: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Optional fields
    stop_loss_price: Mapped[Optional[Numeric]] = mapped_column(Numeric, nullable=True)
    take_profit_price: Mapped[Optional[Numeric]] = mapped_column(Numeric, nullable=True)
    lowest_price_during_trade: Mapped[Optional[Numeric]] = mapped_column(
        Numeric, nullable=True
    )
    highest_price_during_trade: Mapped[Optional[Numeric]] = mapped_column(
        Numeric, nullable=True
    )

    # Timestamps
    created_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    trading_account: Mapped["TradingAccount"] = relationship(
        "TradingAccount", back_populates="trades"
    )
    asset: Mapped[Optional["Asset"]] = relationship("Asset", back_populates="trades")
    platform: Mapped[Optional["Platform"]] = relationship("Platform", back_populates="trades")
    import_run: Mapped[Optional["ImportRun"]] = relationship("ImportRun", back_populates="trades")

    # Recursive relationship
    children: Mapped[List["Trade"]] = relationship(
        "Trade",
        backref=relationship("Trade", remote_side=[id]),
        cascade="all, delete-orphan",
        single_parent=True
    )

    tags: Mapped[list["Tag"]] = relationship(
        secondary="public.trades_tags", back_populates="trades"
    )
    mistakes: Mapped[list["Mistake"]] = relationship(
        "Mistake", secondary="public.trades_mistakes", back_populates="trades"
    )
    playbook: Mapped[Optional["Playbook"]] = relationship("Playbook", back_populates="trades")
    news_impacts: Mapped[list["NewsImpact"]] = relationship(
        "NewsImpact", secondary="public.trades_news_impacts", back_populates="trades"
    )
    psychology_states: Mapped[list["PsychologyState"]] = relationship(
        "PsychologyState", secondary="public.trades_psychology", back_populates="trades"
    )
    notes: Mapped[list["Note"]] = relationship("Note", back_populates="trade")
    images: Mapped[list["Image"]] = relationship("Image", foreign_keys="Image.trade_id", back_populates="trade")
    rules_followed: Mapped[List["RulePlaybook"]] = relationship(
        "RulePlaybook",
        secondary=trades_rules_association,
        back_populates="trades"
    )

    def to_dict(self):
        """
        Converts the trade object to a dictionary, handling data types correctly.
        """
        from decimal import Decimal
        import datetime

        result = {}
        for c in self.__table__.columns:
            value = getattr(self, c.name)
            if isinstance(value, Decimal):
                result[c.name] = float(value)
            elif isinstance(value, (datetime.datetime, datetime.date)):
                result[c.name] = value.isoformat()
            else:
                result[c.name] = value
        return result
