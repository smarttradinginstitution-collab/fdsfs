# app/Models/news_impact.py
from __future__ import annotations

import uuid
from typing import Any, TYPE_CHECKING

from sqlalchemy import String, TIMESTAMP, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.db import Base

if TYPE_CHECKING:
    from app.Models.news_impacts_group import NewsImpactsGroup
    from app.Models.trade import Trade


class NewsImpact(Base):
    __tablename__ = "news_impacts"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.news_impacts_groups.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String, nullable=True)
    color: Mapped[str] = mapped_column(String(7), nullable=False, default="#888888")
    created_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    # Relazioni
    group: Mapped["NewsImpactsGroup"] = relationship(
        "NewsImpactsGroup", back_populates="news_impacts"
    )
    trades: Mapped[list["Trade"]] = relationship(
        "Trade", secondary="public.trades_news_impacts", back_populates="news_impacts"
    )