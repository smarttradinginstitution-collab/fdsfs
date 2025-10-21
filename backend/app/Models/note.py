from __future__ import annotations

import uuid
from typing import Any, TYPE_CHECKING, Optional, List
from datetime import date
from sqlalchemy import String, TIMESTAMP, func, ForeignKey, DATE
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.db import Base
from app.Models.notes_note_templates import notes_note_templates_association

if TYPE_CHECKING:
    from app.Models.notebook_folder import NotebookFolder
    from app.Models.general_account import GeneralAccount
    from app.Models.trade import Trade
    from app.Models.note_template import NoteTemplate


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
        index=True,
    )
    trade_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.trades.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
        index=True,
    )
    note_date: Mapped[Optional[date]] = mapped_column(DATE, nullable=True)
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
    deleted_at: Mapped[Optional[Any]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )

    # Relationships
    folder: Mapped["NotebookFolder"] = relationship(
        "NotebookFolder", back_populates="notes"
    )
    trade: Mapped[Optional["Trade"]] = relationship("Trade", back_populates="notes")
    templates: Mapped[List["NoteTemplate"]] = relationship(
        "NoteTemplate",
        secondary=notes_note_templates_association,
        back_populates="notes",
    )