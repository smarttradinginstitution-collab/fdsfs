from __future__ import annotations
import uuid
import datetime
from sqlalchemy import String, ForeignKey, TIMESTAMP, Numeric, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.Infrastructure.db import Base
from app.Models.account_order_option import AccountOrderOption

class AccountOrder(Base):
    __tablename__ = "account_orders"
    __table_args__ = {"schema": "public"}

    id: Mapped[str] = mapped_column(String, primary_key=True)
    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("public.brokerage_accounts.id", ondelete="CASCADE"))
    symbol: Mapped[str] = mapped_column(String)
    action: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str | None] = mapped_column(String, nullable=True)
    total_quantity: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    open_quantity: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    canceled_quantity: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    filled_quantity: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    execution_price: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    limit_price: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    stop_price: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    order_type: Mapped[str | None] = mapped_column(String, nullable=True)
    time_in_force: Mapped[str | None] = mapped_column(String, nullable=True)
    time_placed: Mapped[datetime.datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    time_updated: Mapped[datetime.datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    time_executed: Mapped[datetime.datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    expiry_date: Mapped[datetime.datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    take_profit_order_id: Mapped[str | None] = mapped_column(String, nullable=True)
    stop_loss_order_id: Mapped[str | None] = mapped_column(String, nullable=True)
    quote_universal_symbol: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    quote_currency: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    account: Mapped["BrokerageAccount"] = relationship(back_populates="orders")
    option_details: Mapped["AccountOrderOption"] = relationship(back_populates="order", cascade="all, delete-orphan", uselist=False)
