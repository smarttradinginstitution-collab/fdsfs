# app/Models/rule_playbook.py
from __future__ import annotations

import uuid
from typing import Any, TYPE_CHECKING, List

from sqlalchemy import TIMESTAMP, ForeignKey, func, Text, Integer, Table, Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.db import Base

if TYPE_CHECKING:
    from app.Models.rules_group_playbook import RulesGroupPlaybook
    from app.Models.trade import Trade


# Many-to-many association table between Trade and RulePlaybook
trades_rules_association = Table(
    'trades_rules',
    Base.metadata,
    Column('trade_id', UUID(as_uuid=True), ForeignKey('public.trades.id', ondelete="CASCADE"), primary_key=True, index=True),
    Column('rule_id', UUID(as_uuid=True), ForeignKey('public.rules_playbook.id', ondelete="CASCADE"), primary_key=True, index=True),
    schema="public"
)


class RulePlaybook(Base):
    __tablename__ = "rules_playbook"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    rules_groups_playbook_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.rules_groups_playbook.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rule: Mapped[str] = mapped_column(Text, nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    # Relazione
    rules_group: Mapped["RulesGroupPlaybook"] = relationship(
        "RulesGroupPlaybook", back_populates="rules"
    )

    trades: Mapped[List["Trade"]] = relationship(
        "Trade",
        secondary=trades_rules_association,
        back_populates="rules_followed"
    )