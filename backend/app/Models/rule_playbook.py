# app/Models/rule_playbook.py
from __future__ import annotations

import uuid
from typing import Any, TYPE_CHECKING

from sqlalchemy import TIMESTAMP, ForeignKey, func, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.db import Base

from app.Models.trades_rules import trades_rules_table

if TYPE_CHECKING:
    from app.Models.rules_group_playbook import RulesGroupPlaybook
    from app.Models.trade import Trade


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
    )
    rule: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    # Relazione
    rules_group: Mapped["RulesGroupPlaybook"] = relationship(
        "RulesGroupPlaybook", back_populates="rules"
    )
    trades: Mapped[list["Trade"]] = relationship(
        "Trade", secondary=trades_rules_table, back_populates="rules"
    )