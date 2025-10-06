# app/Models/asset.py
from __future__ import annotations

import uuid
from typing import Any, Optional, TYPE_CHECKING

from sqlalchemy import String, TIMESTAMP, ForeignKey, func, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import FetchedValue

from app.Infrastructure.db import Base

if TYPE_CHECKING:
    from app.Models.asset_class import AssetClass
    from app.Models.trade import Trade
    from app.Models.asset_alias import AssetAlias
    from app.Models.asset_market import AssetMarket


class Asset(Base):
    __tablename__ = "assets"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    symbol: Mapped[Optional[str]] = mapped_column(String)
    name: Mapped[Optional[str]] = mapped_column(String)
    symbol_norm: Mapped[Optional[str]] = mapped_column(
        Text, server_default=FetchedValue(), nullable=True
    )
    
    asset_class_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.asset_classes.id"),
        nullable=False,
    )
    asset_market_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.asset_markets.id"),
        nullable=False,
    )
    created_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    # Relazioni
    asset_class: Mapped["AssetClass"] = relationship(
        "AssetClass", back_populates="assets"
    )
    asset_market: Mapped["AssetMarket"] = relationship(
        "AssetMarket", back_populates="assets"
    )
    trades: Mapped[list["Trade"]] = relationship("Trade", back_populates="asset")
    aliases: Mapped[list["AssetAlias"]] = relationship(
        "AssetAlias", back_populates="asset", cascade="all, delete-orphan"
    )