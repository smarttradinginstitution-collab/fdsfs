from __future__ import annotations
import uuid
import datetime
from sqlalchemy import String, ForeignKey, TIMESTAMP, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.Infrastructure.db import Base

class AccountBalance(Base):
    __tablename__ = "account_balances"
    __table_args__ = (
        UniqueConstraint('account_id', 'currency_code', name='unique_account_currency'),
        {"schema": "public"}
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("public.brokerage_accounts.id", ondelete="CASCADE"))
    currency_code: Mapped[str] = mapped_column(String, nullable=False)
    cash_amount: Mapped[float] = mapped_column(Numeric, nullable=True)
    buying_power: Mapped[float] = mapped_column(Numeric, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
