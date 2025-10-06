import uuid
from datetime import datetime
from typing import List

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.db import Base


class AssetMarket(Base):
    __tablename__ = "asset_markets"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    assets: Mapped[List["Asset"]] = relationship("Asset", back_populates="asset_market")

    def __repr__(self) -> str:
        return f"<AssetMarket(id={self.id}, name='{self.name}', code='{self.code}')>"