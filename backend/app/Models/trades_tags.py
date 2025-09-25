# app/Models/trades_tags.py
from __future__ import annotations

import uuid
from typing import Any, TYPE_CHECKING

from sqlalchemy import TIMESTAMP, ForeignKey, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.db import Base

if TYPE_CHECKING:
    from app.Models.trade import Trade
    from app.Models.tag import Tag


class TradesTags(Base):
    __tablename__ = "trades_tags"
    __table_args__ = (
        UniqueConstraint("trade_id", "tag_id", name="uq_trades_tags_trade_tag"),
        {"schema": "public"},
    )

    trade_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.trades.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.tags.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    # Relazioni
    trade: Mapped[Trade] = relationship("Trade", back_populates="tag_links")
    tag: Mapped[Tag] = relationship("Tag", back_populates="trade_links")