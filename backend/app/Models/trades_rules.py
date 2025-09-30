# app/Models/trades_rules.py
from __future__ import annotations

import uuid
from typing import Any, TYPE_CHECKING

from sqlalchemy import TIMESTAMP, ForeignKey, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.Infrastructure.db import Base

if TYPE_CHECKING:
    from app.Models.trade import Trade
    from app.Models.rule_playbook import RulePlaybook


class TradesRules(Base):
    __tablename__ = "trades_rules"
    __table_args__ = (
        UniqueConstraint("trade_id", "rule_id", name="uq_trades_rules_trade_rule"),
        {"schema": "public"},
    )

    trade_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.trades.id", ondelete="CASCADE"),
        primary_key=True,
    )
    rule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.rules_playbook.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )