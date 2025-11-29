
# app/Models/playbook_block.py
from __future__ import annotations

import uuid
from typing import Any, TYPE_CHECKING, Optional

from sqlalchemy import TIMESTAMP, func, ForeignKey, String, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.base import Base
from app.Models.enums import PlaybookBlockType

if TYPE_CHECKING:
    from app.Models.playbook import Playbook


class PlaybookBlock(Base):
    __tablename__ = "playbook_blocks"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    playbook_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.playbooks.id", ondelete="CASCADE"),
        nullable=False,
    )
    block_type: Mapped[PlaybookBlockType] = mapped_column(
        Enum(PlaybookBlockType, name='block_type_enum', schema='public', native_enum=True),
        nullable=False,
        default=PlaybookBlockType.RULES
    )
    title: Mapped[str] = mapped_column(String, nullable=False, default="New Block")
    content: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        default=lambda: {"groups": []} # Default to the new structure
    )
    created_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationship
    playbook: Mapped["Playbook"] = relationship(
        "Playbook", back_populates="blocks"
    )
