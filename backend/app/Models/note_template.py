from __future__ import annotations

import uuid
from typing import Any, TYPE_CHECKING, Optional, List

from sqlalchemy import TIMESTAMP, func, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.db import Base
from app.Models.Bridge.notes_note_templates import notes_note_templates_association

if TYPE_CHECKING:
    from app.Models.general_account import GeneralAccount
    from app.Models.note import Note


class NoteTemplate(Base):
    __tablename__ = "note_templates"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    general_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.general_accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url_image: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
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
    general_account: Mapped["GeneralAccount"] = relationship("GeneralAccount")
    notes: Mapped[List["Note"]] = relationship(
        "Note", secondary=notes_note_templates_association, back_populates="templates"
    )