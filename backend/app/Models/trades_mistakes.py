# app/Models/trades_mistakes.py
from __future__ import annotations

import uuid
from typing import Any, TYPE_CHECKING

from sqlalchemy import TIMESTAMP, ForeignKey, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.db import Base

if TYPE_CHECKING:
    from app.Models.trade import Trade
    from app.Models.mistake import Mistake


class TradesMistakes(Base):
    __tablename__ = "trades_mistakes"
    __table_args__ = (
        UniqueConstraint("trade_id", "mistake_id", name="uq_trades_mistakes_trade_mistake"),
        {"schema": "public"},
    )

    trade_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.trades.id", ondelete="CASCADE"),
        primary_key=True,
    )
    mistake_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.mistakes.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    # Relazioni
    trade: Mapped["Trade"] = relationship("Trade", back_populates="mistake_links")
    mistake: Mapped["Mistake"] = relationship("Mistake", back_populates="trade_links")