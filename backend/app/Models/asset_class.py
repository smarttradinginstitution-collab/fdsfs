# app/Models/asset_class.py
from __future__ import annotations

import uuid
from typing import Any, TYPE_CHECKING

from sqlalchemy import String, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.base import Base

if TYPE_CHECKING:
    from app.Models.asset import Asset
    from app.Models.broker_asset_class import BrokerAssetClass


class AssetClass(Base):
    __tablename__ = "asset_classes"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    created_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    # Relazioni
    assets: Mapped[list["Asset"]] = relationship(
        "Asset", back_populates="asset_class", cascade="all, delete-orphan"
    )
    brokers_association: Mapped[list[BrokerAssetClass]] = relationship(
        "BrokerAssetClass", back_populates="asset_class", cascade="all, delete-orphan"
    )
