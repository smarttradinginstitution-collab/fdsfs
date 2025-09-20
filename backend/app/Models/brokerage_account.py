from __future__ import annotations
import uuid
import datetime
from sqlalchemy import String, ForeignKey, TIMESTAMP, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.Infrastructure.db import Base

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
