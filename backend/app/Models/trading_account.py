# app/Models/trading_account.py
from __future__ import annotations

import uuid
from typing import Any, Optional, TYPE_CHECKING

from sqlalchemy import String, TIMESTAMP, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.db import Base

if TYPE_CHECKING:
    from app.Models.general_account import GeneralAccount
    from app.Models.broker import Broker
    from app.Models.trade import Trade


class TradingAccount(Base):
    __tablename__ = "trading_accounts"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    general_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.general_accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    broker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("public.brokers.id"),
        nullable=False,
    )
    label: Mapped[Optional[str]] = mapped_column(String)
    initial_balance: Mapped[Optional[float]] = mapped_column()
    total_pnl: Mapped[Optional[float]] = mapped_column(default=0)
    total_pnl: Mapped[Optional[float]] = mapped_column(default=0)
    currency: Mapped[Optional[str]] = mapped_column(String(3))
    created_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    # Relazioni
    general_account: Mapped["GeneralAccount"] = relationship(
        "GeneralAccount", back_populates="trading_accounts"
    )
    broker: Mapped[Optional["Broker"]] = relationship(
        "Broker", back_populates="trading_accounts"
    )
    trades: Mapped[list["Trade"]] = relationship(
        "Trade", back_populates="trading_account"
    )