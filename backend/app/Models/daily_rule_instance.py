# backend/app/Models/daily_rule_instance.py
from __future__ import annotations

import uuid
from typing import Any, TYPE_CHECKING, Optional

from sqlalchemy import (
    Text,
    TIMESTAMP,
    ForeignKey,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.db import Base

if TYPE_CHECKING:
    from app.Models.note import Note
    from app.Models.discipline_rule import DisciplineRule


class DailyRuleInstance(Base):
    __tablename__ = "daily_rule_instances"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    daily_journal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.notes.id", ondelete="CASCADE"),
        nullable=False,
    )
    rule_template_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.discipline_rules.id", ondelete="SET NULL"),
        nullable=True,
    )

    name: Mapped[str] = mapped_column(Text, nullable=False)
    rule_type: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="pending")
    actual_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    daily_journal: Mapped["Note"] = relationship(
        "Note", back_populates="daily_rule_instances"
    )
    rule_template: Mapped[Optional["DisciplineRule"]] = relationship(
        "DisciplineRule", back_populates="daily_instances"
    )