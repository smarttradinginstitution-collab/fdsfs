from __future__ import annotations
import uuid
from typing import Any, TYPE_CHECKING, List
from sqlalchemy import String, TIMESTAMP, func, ForeignKey, Text, INT
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.Infrastructure.db import Base

if TYPE_CHECKING:
    from app.Models.general_account import GeneralAccount

class ManualRule(Base):
    __tablename__ = "manual_rules"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    general_account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("public.general_accounts.id", ondelete="CASCADE"), nullable=False)

    name: Mapped[str] = mapped_column(Text, nullable=False)
    frequency: Mapped[List[int]] = mapped_column(ARRAY(INT), nullable=False) # e.g., [1,2,3,4,5] for Mon-Fri

    created_at: Mapped[Any] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[Any] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    general_account: Mapped["GeneralAccount"] = relationship("GeneralAccount", back_populates="manual_rules")

# Add the relationship to GeneralAccount model
from app.Models.general_account import GeneralAccount
GeneralAccount.manual_rules = relationship("ManualRule", order_by=ManualRule.id, back_populates="general_account")