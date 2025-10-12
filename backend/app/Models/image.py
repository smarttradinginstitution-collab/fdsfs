from __future__ import annotations
import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import func, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.Infrastructure.db import Base
from sqlalchemy.dialects.postgresql import UUID

if TYPE_CHECKING:
    from app.Models.general_account import GeneralAccount
    from app.Models.trade import Trade

class Image(Base):
    __tablename__ = "images"
    __table_args__ = {"comment": "Stores metadata for user-uploaded images, now integrated with Supabase Storage and linked to trades for advanced visual journaling."}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    general_account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("public.general_accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    trade_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("public.trades.id", ondelete="SET NULL"), nullable=True, index=True
    )
    filename: Mapped[str] = mapped_column(String, nullable=False)
    storage_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    url: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phase: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_primary_before: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_primary_after: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # --- Relationships ---
    general_account: Mapped["GeneralAccount"] = relationship(back_populates="images")
    trade: Mapped["Trade | None"] = relationship("Trade", foreign_keys="Image.trade_id", back_populates="images")