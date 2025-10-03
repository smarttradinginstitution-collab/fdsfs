from __future__ import annotations

import uuid
from typing import Any, TYPE_CHECKING, Optional

from sqlalchemy import String, TIMESTAMP, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.db import Base

if TYPE_CHECKING:
    from app.Models.notebook_folder import NotebookFolder
    from app.Models.general_account import GeneralAccount
    from app.Models.trade import Trade


class Note(Base):
    __tablename__ = "notes"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    folder_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.notebook_folders.id", ondelete="CASCADE"),
        nullable=False,
    )
    general_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.general_accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    trade_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.trades.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    folder: Mapped["NotebookFolder"] = relationship(
        "NotebookFolder", back_populates="notes"
    )
    general_account: Mapped["GeneralAccount"] = relationship(
        "GeneralAccount", back_populates="notes"
    )
    trade: Mapped[Optional["Trade"]] = relationship("Trade", back_populates="notes")