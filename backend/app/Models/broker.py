# app/Models/broker.py
from __future__ import annotations

import uuid
from typing import Any, TYPE_CHECKING

from sqlalchemy import String, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.db import Base

if TYPE_CHECKING:
    from app.Models.trading_account import TradingAccount
    from app.Models.platform import Platform
    from app.Models.asset_alias import AssetAlias
    from app.Models.broker_asset_class import BrokerAssetClass

class Broker(Base):
    __tablename__ = "brokers"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    created_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    trading_accounts: Mapped[list["TradingAccount"]] = relationship(
        "TradingAccount", back_populates="broker"
    )
    platforms: Mapped[list["Platform"]] = relationship(
        secondary="public.broker_platforms", back_populates="brokers"
    )
    asset_aliases: Mapped[list["AssetAlias"]] = relationship(
        "AssetAlias", back_populates="broker", cascade="all, delete-orphan"
    )
    asset_classes_association: Mapped[list["BrokerAssetClass"]] = relationship(
        "BrokerAssetClass",
        back_populates="broker",
        cascade="all, delete-orphan",
    )
