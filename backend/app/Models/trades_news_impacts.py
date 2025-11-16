# app/Models/trades_news_impacts.py
from __future__ import annotations

import uuid
from typing import Any, TYPE_CHECKING

from sqlalchemy import TIMESTAMP, ForeignKey, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.base import Base

if TYPE_CHECKING:
    from app.Models.trade import Trade
    from app.Models.news_impact import NewsImpact


class TradesNewsImpacts(Base):
    __tablename__ = "trades_news_impacts"
    __table_args__ = (
        UniqueConstraint("trade_id", "news_impact_id", name="uq_trades_news_impacts_trade_news_impact"),
        {"schema": "public"},
    )

    trade_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.trades.id", ondelete="CASCADE"),
        primary_key=True,
    )
    news_impact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.news_impacts.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    # Le relazioni qui sono state rimosse per risolvere l'ambiguità.