# app/Models/brokerage_connection.py

from __future__ import annotations
import uuid
import datetime
from sqlalchemy import String, ForeignKey, TIMESTAMP, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.Infrastructure.db import Base

class BrokerageConnection(Base):
    __tablename__ = "brokerage_connections"
    __table_args__ = {"schema": "public", "extend_existing": True}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("public.profiles.id", ondelete="CASCADE"))
    brokerage_name: Mapped[str] = mapped_column(String)
    brokerage_display_name: Mapped[str] = mapped_column(String, nullable=True)
    brokerage_logo_url: Mapped[str] = mapped_column(String, nullable=True)
    connection_type: Mapped[str] = mapped_column(String)
    disabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    disabled_date: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    deleted_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    manual_refresh_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    last_manual_refresh_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    # Relationship to Profile (many-to-one)
    profile: Mapped["Profile"] = relationship(back_populates="brokerage_connections")
