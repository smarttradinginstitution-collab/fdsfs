from __future__ import annotations
import uuid
from typing import Any, TYPE_CHECKING
from sqlalchemy import String, TIMESTAMP, func, ForeignKey, Text, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.Infrastructure.base import Base

if TYPE_CHECKING:
    from app.Models.manual_rule import ManualRule
    from app.Models.trading_account import TradingAccount
    from app.Models.note import Note

class DailyRuleInstance(Base):
    __tablename__ = "daily_rule_instances"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    manual_rule_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("public.manual_rules.id", ondelete="CASCADE"), nullable=False)
    trading_account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("public.trading_accounts.id", ondelete="CASCADE"), nullable=False)
    daily_journal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("public.notes.id", ondelete="CASCADE"), nullable=False)

    date: Mapped[Any] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default='pending')

    created_at: Mapped[Any] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[Any] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    rule_template: Mapped["ManualRule"] = relationship("ManualRule")
    trading_account: Mapped["TradingAccount"] = relationship("TradingAccount")
    daily_journal: Mapped["Note"] = relationship("Note")