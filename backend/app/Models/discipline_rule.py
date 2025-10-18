from __future__ import annotations
import uuid
from typing import Any, TYPE_CHECKING, List, Optional
from sqlalchemy import String, TIMESTAMP, func, ForeignKey, Text, INT
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.Infrastructure.db import Base

if TYPE_CHECKING:
    from app.Models.general_account import GeneralAccount
    from app.Models.daily_rule_instance import DailyRuleInstance

class DisciplineRule(Base):
    __tablename__ = "discipline_rules"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    general_account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("public.general_accounts.id", ondelete="CASCADE"), nullable=False)

    rule_type: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    condition_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    condition_value: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    active_days: Mapped[List[int]] = mapped_column(ARRAY(INT), nullable=False)

    created_at: Mapped[Any] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[Any] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    general_account: Mapped["GeneralAccount"] = relationship("GeneralAccount", back_populates="discipline_rules")
    daily_instances: Mapped[List["DailyRuleInstance"]] = relationship("DailyRuleInstance", back_populates="rule_template")

# Add the relationship to GeneralAccount model
from app.Models.general_account import GeneralAccount
GeneralAccount.discipline_rules = relationship("DisciplineRule", order_by=DisciplineRule.id, back_populates="general_account")