# app/Models/trades_playbooks.py
from __future__ import annotations

import uuid
from typing import Any, TYPE_CHECKING

from sqlalchemy import TIMESTAMP, ForeignKey, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.db import Base

if TYPE_CHECKING:
    from app.Models.trade import Trade
    from app.Models.playbook import Playbook


class TradesPlaybooks(Base):
    __tablename__ = "trades_playbooks"
    __table_args__ = (
        UniqueConstraint("trade_id", "playbook_id", name="uq_trades_playbooks_trade_playbook"),
        {"schema": "public"},
    )

    trade_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.trades.id", ondelete="CASCADE"),
        primary_key=True,
    )
    playbook_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.playbooks.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    # Relazioni
    trade: Mapped["Trade"] = relationship("Trade")
    playbook: Mapped["Playbook"] = relationship("Playbook")