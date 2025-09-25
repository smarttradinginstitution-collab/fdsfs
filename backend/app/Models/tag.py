# app/Models/tag.py
from __future__ import annotations

import uuid
from typing import Optional, TYPE_CHECKING, Any

from sqlalchemy import String, ForeignKey, func, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.db import Base

if TYPE_CHECKING:
    from app.Models.general_account import GeneralAccount


class Tag(Base):
    __tablename__ = "tags"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    general_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.general_accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True, default="#888888")
    created_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    # Relazioni
    general_account: Mapped["GeneralAccount"] = relationship(
        "GeneralAccount", back_populates="tags"
    )
    trades: Mapped[list["Trade"]] = relationship(
        secondary="public.trades_tags", back_populates="tags"
    )