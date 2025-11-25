# app/Models/platform.py
from __future__ import annotations

import uuid
from typing import Any, TYPE_CHECKING

from sqlalchemy import TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID, CITEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.base import Base

if TYPE_CHECKING:
    from app.Models.trade import Trade
    from app.Models.broker import Broker
    from app.Models.asset_alias import AssetAlias

class Platform(Base):
    __tablename__ = "platforms"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(CITEXT, nullable=False, unique=True)
    created_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    trades: Mapped[list["Trade"]] = relationship("Trade", back_populates="platform")
    brokers: Mapped[list["Broker"]] = relationship(
        secondary="public.broker_platforms", back_populates="platforms"
    )
    asset_aliases: Mapped[list["AssetAlias"]] = relationship(
        "AssetAlias", back_populates="platform", cascade="all, delete-orphan"
    )