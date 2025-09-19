# app/Models/brokerage_connection.py

from __future__ import annotations
import uuid
import datetime
from sqlalchemy import String, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.Infrastructure.db import Base

class BrokerageConnection(Base):
    __tablename__ = "brokerage_connections"
    __table_args__ = {"schema": "public", "extend_existing": True}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("auth.users.id"))
    snaptrade_connection_id: Mapped[str] = mapped_column(String)
    brokerage_name: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.datetime.utcnow)

    # Relationship to AuthUser (many-to-one)
    user: Mapped["AuthUser"] = relationship(back_populates="brokerage_connections")
