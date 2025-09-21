from __future__ import annotations
import uuid
import datetime
from sqlalchemy import String, ForeignKey, TIMESTAMP, Numeric, func, Date, Boolean, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.Infrastructure.db import Base

class AccountOrderOption(Base):
    __tablename__ = "account_order_options"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    account_order_id: Mapped[str] = mapped_column(String, ForeignKey("public.account_orders.id", ondelete="CASCADE"), unique=True, nullable=False)
    option_ticker: Mapped[str] = mapped_column(String, nullable=False)
    option_type: Mapped[str | None] = mapped_column(String)
    strike_price: Mapped[float | None] = mapped_column(Numeric)
    expiration_date: Mapped[datetime.date | None] = mapped_column(Date)
    is_mini_option: Mapped[bool | None] = mapped_column(Boolean)
    underlying_security_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("public.securities.id", ondelete="SET NULL"))
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # The back-populating relationship to AccountOrder is defined in the AccountOrder model.
    order: Mapped["AccountOrder"] = relationship(back_populates="option_details")
    underlying_security: Mapped["Security"] = relationship()
