from __future__ import annotations
import uuid
import datetime
from sqlalchemy import String, ForeignKey, TIMESTAMP, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.Infrastructure.db import Base
from app.Models.account_position import AccountPosition
from app.Models.account_balance import AccountBalance
from app.Models.account_order import AccountOrder

class BrokerageAccount(Base):
    __tablename__ = "brokerage_accounts"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("public.profiles.id", ondelete="CASCADE"))
    connection_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("public.brokerage_connections.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String)
    number: Mapped[str] = mapped_column(String)
    balance: Mapped[float] = mapped_column(Numeric)
    currency: Mapped[str] = mapped_column(String)
    institution_name: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)

    # Relationship to Profile (many-to-one)
    profile: Mapped["Profile"] = relationship(back_populates="brokerage_accounts")

    # Relationship to BrokerageConnection (many-to-one)
    connection: Mapped["BrokerageConnection"] = relationship(back_populates="brokerage_accounts")

    # Relationships to holdings (one-to-many)
    positions: Mapped[list["AccountPosition"]] = relationship("AccountPosition", back_populates="account", cascade="all, delete-orphan")
    balances: Mapped[list["AccountBalance"]] = relationship("AccountBalance", back_populates="account", cascade="all, delete-orphan")
    orders: Mapped[list["AccountOrder"]] = relationship("AccountOrder", back_populates="account", cascade="all, delete-orphan")
