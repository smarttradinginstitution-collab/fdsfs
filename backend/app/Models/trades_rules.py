from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    TIMESTAMP,
    func,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID

from app.Infrastructure.db import Base

trades_rules_table = Table(
    "trades_rules",
    Base.metadata,
    Column(
        "trade_id",
        UUID(as_uuid=True),
        ForeignKey("public.trades.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "rule_id",
        UUID(as_uuid=True),
        ForeignKey("public.rules_playbook.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "created_at",
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    UniqueConstraint("trade_id", "rule_id", name="uq_trades_rules_trade_rule"),
    schema="public",
)