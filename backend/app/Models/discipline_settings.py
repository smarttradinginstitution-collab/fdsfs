from __future__ import annotations
import uuid
import datetime
from typing import Any, TYPE_CHECKING, List, Optional
from sqlalchemy import String, TIMESTAMP, func, ForeignKey, Text, INT, Time, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.Infrastructure.base import Base

if TYPE_CHECKING:
    from app.Models.general_account import GeneralAccount

class DisciplineSettings(Base):
    __tablename__ = "discipline_settings"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    general_account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("public.general_accounts.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Global settings
    trading_days: Mapped[List[int]] = mapped_column(ARRAY(INT), nullable=False, default=[1, 2, 3, 4, 5])

    # Automated rules
    start_day_by: Mapped[Optional[datetime.time]] = mapped_column(Time, nullable=True)
    link_trades_to_playbook_threshold: Mapped[Optional[int]] = mapped_column(INT, nullable=True)
    trade_has_stop_loss_threshold: Mapped[Optional[int]] = mapped_column(INT, nullable=True)

    max_loss_per_trade_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # '%' or '$'
    max_loss_per_trade_value: Mapped[Optional[Float]] = mapped_column(Float, nullable=True)

    max_loss_per_day: Mapped[Optional[Float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[Any] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[Any] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    general_account: Mapped["GeneralAccount"] = relationship("GeneralAccount", back_populates="discipline_settings")

# Add the relationship to GeneralAccount model
from app.Models.general_account import GeneralAccount
GeneralAccount.discipline_settings = relationship("DisciplineSettings", uselist=False, back_populates="general_account")