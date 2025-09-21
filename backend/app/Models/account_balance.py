from __future__ import annotations
import uuid
import datetime
from sqlalchemy import String, ForeignKey, TIMESTAMP, Numeric, PrimaryKeyConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.Infrastructure.db import Base

class AccountBalance(Base):
    __tablename__ = "account_balances"
    __table_args__ = (
        PrimaryKeyConstraint('account_id', 'currency_code', name='account_balances_pkey'),
        {"schema": "public"},
    )

    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("public.brokerage_accounts.id", ondelete="CASCADE"))
    currency_code: Mapped[str] = mapped_column(String)
    cash_amount: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    buying_power: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationship to BrokerageAccount (many-to-one)
    account: Mapped["BrokerageAccount"] = relationship(back_populates="balances")
