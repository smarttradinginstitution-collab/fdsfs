
# app/Models/playbook.py
from __future__ import annotations

import uuid
from typing import Any, TYPE_CHECKING, Optional

from sqlalchemy import String, TIMESTAMP, ForeignKey, func, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.base import Base

if TYPE_CHECKING:
    from app.Models.general_account import GeneralAccount
    from app.Models.trade import Trade
    from app.Models.playbook_block import PlaybookBlock
    from app.Models.image import Image


class Playbook(Base):
    __tablename__ = "playbooks"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    general_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.general_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    private: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    color: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    icon_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    # Relazioni
    general_account: Mapped["GeneralAccount"] = relationship(
        "GeneralAccount", back_populates="playbooks"
    )
    trades: Mapped[list["Trade"]] = relationship("Trade", back_populates="playbook")

    # New relationships to blocks
    blocks: Mapped[list["PlaybookBlock"]] = relationship(
        "PlaybookBlock",
        back_populates="playbook",
        cascade="all, delete-orphan",
    )
    # Relationship to ideal images
    ideal_images: Mapped[list["Image"]] = relationship(
        "Image",
        back_populates="playbook",
        cascade="all, delete-orphan",
    )
