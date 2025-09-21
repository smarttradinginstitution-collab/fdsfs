from __future__ import annotations
import uuid
import datetime
from sqlalchemy import String, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.Infrastructure.db import Base

class Security(Base):
    __tablename__ = "securities"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    symbol: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    currency_code: Mapped[str | None] = mapped_column(String, nullable=True)
    exchange_name: Mapped[str | None] = mapped_column(String, nullable=True)
    figi_code: Mapped[str | None] = mapped_column(String, nullable=True)
    raw_symbol: Mapped[str | None] = mapped_column(String, nullable=True)
    mic_code: Mapped[str | None] = mapped_column(String, nullable=True)
    timezone: Mapped[str | None] = mapped_column(String, nullable=True)
    start_time: Mapped[str | None] = mapped_column(String, nullable=True)
    close_time: Mapped[str | None] = mapped_column(String, nullable=True)
    suffix: Mapped[str | None] = mapped_column(String, nullable=True)
    type_code: Mapped[str | None] = mapped_column(String, nullable=True)
    type_description: Mapped[str | None] = mapped_column(String, nullable=True)
    figi_share_class: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationship to AccountPosition (one-to-many)
    positions: Mapped[list["AccountPosition"]] = relationship(back_populates="security")
