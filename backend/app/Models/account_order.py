from __future__ import annotations
import uuid
import datetime
from sqlalchemy import String, ForeignKey, TIMESTAMP, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.Infrastructure.db import Base

class AccountOrder(Base):
    __tablename__ = "account_orders"
    __table_args__ = {"schema": "public"}

    id: Mapped[str] = mapped_column(String, primary_key=True)
    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("public.brokerage_accounts.id", ondelete="CASCADE"))
    symbol: Mapped[str] = mapped_column(String)
    action: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str | None] = mapped_column(String, nullable=True)
    total_quantity: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    filled_quantity: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    execution_price: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    limit_price: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    time_placed: Mapped[datetime.datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)

    # Relationship to BrokerageAccount (many-to-one)
    account: Mapped["BrokerageAccount"] = relationship(back_populates="orders")
