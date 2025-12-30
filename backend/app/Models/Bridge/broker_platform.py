# app/Models/broker_platform.py
from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import TIMESTAMP, ForeignKey, func, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.Infrastructure.db import Base

class BrokerPlatform(Base):
    __tablename__ = "broker_platforms"
    __table_args__ = (
        PrimaryKeyConstraint('broker_id', 'platform_id'),
        {"schema": "public"}
    )

    broker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.brokers.id", ondelete="CASCADE"),
        nullable=False
    )
    platform_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.platforms.id", ondelete="CASCADE"),
        nullable=False
    )
    created_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )