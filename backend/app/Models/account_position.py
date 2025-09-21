from __future__ import annotations
import uuid
import datetime
from sqlalchemy import String, ForeignKey, TIMESTAMP, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.Infrastructure.db import Base

class AccountPosition(Base):
    __tablename__ = "account_positions"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("public.brokerage_accounts.id", ondelete="CASCADE"))
    symbol: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    units: Mapped[float] = mapped_column(Numeric)
    price: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    currency: Mapped[str | None] = mapped_column(String, nullable=True)
    open_pnl: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    average_purchase_price: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)

    # Relationship to BrokerageAccount (many-to-one)
    account: Mapped["BrokerageAccount"] = relationship(back_populates="positions")
