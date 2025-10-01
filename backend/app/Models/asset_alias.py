# app/Models/asset_alias.py
from __future__ import annotations

import uuid
from typing import Any, Optional, TYPE_CHECKING

from sqlalchemy import TIMESTAMP, ForeignKey, func, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.db import Base

if TYPE_CHECKING:
    from app.Models.asset import Asset
    from app.Models.broker import Broker
    from app.Models.platform import Platform

class AssetAlias(Base):
    __tablename__ = "asset_aliases"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("public.assets.id", ondelete="CASCADE"), nullable=False
    )
    broker_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("public.brokers.id", ondelete="CASCADE"), nullable=True
    )
    platform_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("public.platforms.id", ondelete="CASCADE"), nullable=True
    )
    alias: Mapped[str] = mapped_column(Text, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default='false')
    created_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    asset: Mapped["Asset"] = relationship("Asset", back_populates="aliases")
    broker: Mapped[Optional["Broker"]] = relationship("Broker", back_populates="asset_aliases")
    platform: Mapped[Optional["Platform"]] = relationship("Platform", back_populates="asset_aliases")

# Add back-population to Asset model if not present
# In app/Models/asset.py, add:
# aliases: Mapped[list["AssetAlias"]] = relationship("AssetAlias", back_populates="asset", cascade="all, delete-orphan")