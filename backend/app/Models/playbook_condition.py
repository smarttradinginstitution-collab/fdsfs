# app/Models/playbook_condition.py
from __future__ import annotations

import uuid
from typing import Any, TYPE_CHECKING, Optional, List

from sqlalchemy import TIMESTAMP, func, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.base import Base

if TYPE_CHECKING:
    from app.Models.playbook import Playbook
    from app.Models.trade_condition_check import TradeConditionCheck


class PlaybookCondition(Base):
    __tablename__ = "playbook_conditions"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    playbook_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.playbooks.id", ondelete="CASCADE"),
        nullable=False,
    )
    category: Mapped[str] = mapped_column(Text, nullable=False)
    variable: Mapped[str] = mapped_column(Text, nullable=False)
    operator: Mapped[str] = mapped_column(Text, nullable=False)
    value: Mapped[dict] = mapped_column(JSONB, nullable=False)
    order: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    playbook: Mapped["Playbook"] = relationship(
        "Playbook", back_populates="conditions"
    )
    trade_checks: Mapped[List["TradeConditionCheck"]] = relationship(
        "TradeConditionCheck",
        back_populates="condition",
        cascade="all, delete-orphan",
    )
