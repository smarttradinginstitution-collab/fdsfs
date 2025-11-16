# app/Models/trade_condition_check.py
from __future__ import annotations

import uuid
from typing import Any, TYPE_CHECKING, Optional

from sqlalchemy import TIMESTAMP, func, ForeignKey, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.base import Base

if TYPE_CHECKING:
    from app.Models.trade import Trade
    from app.Models.playbook_condition import PlaybookCondition


class TradeConditionCheck(Base):
    __tablename__ = "trade_condition_checks"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    trade_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.trades.id", ondelete="CASCADE"),
        nullable=False,
    )
    condition_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.playbook_conditions.id", ondelete="CASCADE"),
        nullable=False,
    )
    was_met: Mapped[bool] = mapped_column(Boolean, nullable=False)
    live_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    trade: Mapped["Trade"] = relationship(
        "Trade", back_populates="condition_checks"
    )
    condition: Mapped["PlaybookCondition"] = relationship(
        "PlaybookCondition", back_populates="trade_checks"
    )
