# app/Models/news_impacts_group.py
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import String, ForeignKey, func, TIMESTAMP, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.base import Base

if TYPE_CHECKING:
    from app.Models.general_account import GeneralAccount
    from app.Models.news_impact import NewsImpact


class NewsImpactsGroup(Base):
    __tablename__ = "news_impacts_groups"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    general_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.general_accounts.id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String, nullable=True, default="#888888")
    position: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
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
    general_account: Mapped["GeneralAccount"] = relationship(
        "GeneralAccount", back_populates="news_impacts_groups"
    )
    news_impacts: Mapped[list["NewsImpact"]] = relationship(
        "NewsImpact",
        back_populates="group",
        cascade="all, delete-orphan",
    )
