# app/Models/news_impact.py
from __future__ import annotations

import uuid
from typing import Any, TYPE_CHECKING

from sqlalchemy import String, TIMESTAMP, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.db import Base

if TYPE_CHECKING:
    from app.Models.general_account import GeneralAccount
    from app.Models.trades_news_impacts import TradesNewsImpacts


class NewsImpact(Base):
    __tablename__ = "news_impacts"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    general_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.general_accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    # Relazioni
    general_account: Mapped["GeneralAccount"] = relationship(
        "GeneralAccount", back_populates="news_impacts"
    )
    trade_links: Mapped[list["TradesNewsImpacts"]] = relationship(
        "TradesNewsImpacts",
        back_populates="news_impact",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )