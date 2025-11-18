# app/Models/trades_psychology.py
from __future__ import annotations

import uuid
from typing import Any, TYPE_CHECKING

from sqlalchemy import TIMESTAMP, ForeignKey, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.base import Base

if TYPE_CHECKING:
    from app.Models.trade import Trade
    from app.Models.psychology_state import PsychologyState


class TradesPsychology(Base):
    __tablename__ = "trades_psychology"
    __table_args__ = (
        UniqueConstraint("trade_id", "psychology_id", name="uq_trades_psychology_trade_psychology"),
        {"schema": "public"},
    )

    trade_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.trades.id", ondelete="CASCADE"),
        primary_key=True,
    )
    psychology_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.psychology_states.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    # Le relazioni qui sono state rimosse per risolvere l'ambiguità.