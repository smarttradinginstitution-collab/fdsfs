# app/Models/rules_group_playbook.py
from __future__ import annotations

import uuid
from typing import Any, TYPE_CHECKING, List

from sqlalchemy import String, TIMESTAMP, ForeignKey, func, Text, UniqueConstraint, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.db import Base

if TYPE_CHECKING:
    from app.Models.playbook import Playbook
    from app.Models.rule_playbook import RulePlaybook


class RulesGroupPlaybook(Base):
    __tablename__ = "rules_groups_playbook"
    __table_args__ = (
        UniqueConstraint('playbook_id', 'name_group', name='uq_group_name_per_playbook'),
        {"schema": "public"}
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    playbook_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.playbooks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name_group: Mapped[str] = mapped_column(Text, nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    # Relazioni
    playbook: Mapped["Playbook"] = relationship(
        "Playbook", back_populates="rules_groups"
    )
    rules: Mapped[List["RulePlaybook"]] = relationship(
        "RulePlaybook",
        back_populates="rules_group",
        cascade="all, delete-orphan",
        lazy="joined" # Usiamo joined per caricare sempre le regole con il gruppo
    )