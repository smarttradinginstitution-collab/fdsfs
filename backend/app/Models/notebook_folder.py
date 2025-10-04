from __future__ import annotations

import uuid
from typing import Any, TYPE_CHECKING, List, Optional

from sqlalchemy import String, TIMESTAMP, func, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.db import Base
from app.Models.enums import FolderType

if TYPE_CHECKING:
    from app.Models.general_account import GeneralAccount
    from app.Models.note import Note


class NotebookFolder(Base):
    __tablename__ = "notebook_folders"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    general_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.general_accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    # Correctly define the column using SQLAlchemy's Enum type
    folder_type: Mapped[FolderType] = mapped_column(
        Enum(FolderType, name="folder_type", create_type=False),
        nullable=False,
        default=FolderType.USER,
    )
    template_content: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
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
    general_account: Mapped["GeneralAccount"] = relationship(
        "GeneralAccount", back_populates="notebook_folders"
    )
    notes: Mapped[List["Note"]] = relationship(
        "Note",
        back_populates="folder",
        cascade="all, delete-orphan",
    )