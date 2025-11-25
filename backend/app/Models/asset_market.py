from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.Infrastructure.base import Base
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from app.Models.asset import Asset  # noqa: F401

import uuid
from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

class AssetMarket(Base):
    __tablename__ = "asset_markets"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    assets: Mapped[List["Asset"]] = relationship("Asset", back_populates="asset_market")