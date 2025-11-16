from __future__ import annotations

import uuid
from typing import Any, TYPE_CHECKING

from sqlalchemy import TIMESTAMP, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.base import Base

if TYPE_CHECKING:
    from app.Models.broker import Broker
    from app.Models.asset_class import AssetClass


class BrokerAssetClass(Base):
    __tablename__ = "broker_asset_classes"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    broker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("public.brokers.id"), nullable=False
    )
    asset_class_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("public.asset_classes.id"), nullable=False
    )
    created_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    broker: Mapped[Broker] = relationship(
        "Broker", back_populates="asset_classes_association"
    )
    asset_class: Mapped[AssetClass] = relationship(
        "AssetClass", back_populates="brokers_association"
    )
