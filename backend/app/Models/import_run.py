# app/Models/import_run.py
from __future__ import annotations

import uuid
from typing import Any, Optional, TYPE_CHECKING

from sqlalchemy import TIMESTAMP, ForeignKey, func, Integer, Text, Enum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.db import Base
from app.Models.enums import ImportSourceType  # Use centralized ENUMs

if TYPE_CHECKING:
    from app.Models.auth_user import AuthUser
    from app.Models.trading_account import TradingAccount
    from app.Models.platform import Platform
    from app.Models.trade import Trade


class ImportRun(Base):
    __tablename__ = "import_runs"
    __table_args__ = (
        UniqueConstraint('file_sha256', 'trading_account_id', name='uq_import_runs_hash_account'),
        {"schema": "public"}
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False
    )
    trading_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("public.trading_accounts.id", ondelete="CASCADE"), nullable=False
    )
    platform_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("public.platforms.id"), nullable=True
    )

    source_type: Mapped[ImportSourceType] = mapped_column(
        Enum(ImportSourceType, name="import_source_type", schema="public"),
        nullable=False
    )
    file_name: Mapped[Optional[str]] = mapped_column(Text)
    # unique=True removed in favor of composite constraint
    file_sha256: Mapped[Optional[str]] = mapped_column(Text)

    status: Mapped[str] = mapped_column(Text, nullable=False, default="queued")
    total_rows: Mapped[int] = mapped_column(Integer, default=0)
    inserted_count: Mapped[int] = mapped_column(Integer, default=0)
    updated_count: Mapped[int] = mapped_column(Integer, default=0)
    skipped_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    # New field for grouping setting
    grouping_tolerance: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    created_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    finished_at: Mapped[Optional[Any]] = mapped_column(TIMESTAMP(timezone=True))

    # Relationships
    user: Mapped["AuthUser"] = relationship("AuthUser")
    trading_account: Mapped["TradingAccount"] = relationship("TradingAccount")
    platform: Mapped[Optional["Platform"]] = relationship("Platform")
    trades: Mapped[list["Trade"]] = relationship("Trade", back_populates="import_run")
