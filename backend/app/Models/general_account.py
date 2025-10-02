# app/Models/general_account.py
from __future__ import annotations

import uuid
from typing import Any, TYPE_CHECKING

from sqlalchemy import String, TIMESTAMP, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.db import Base

if TYPE_CHECKING:
    from app.Models.auth_user import AuthUser
    from app.Models.trading_account import TradingAccount
    from app.Models.tags_group import TagsGroup
    from app.Models.mistake import Mistake
    from app.Models.psychology_state import PsychologyState
    from app.Models.news_impact import NewsImpact
    from app.Models.playbook import Playbook


class GeneralAccount(Base):
    __tablename__ = "general_accounts"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    label: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    # Relazioni
    user: Mapped["AuthUser"] = relationship(back_populates="general_account")
    trading_accounts: Mapped[list["TradingAccount"]] = relationship(
        "TradingAccount", back_populates="general_account"
    )
    tags_groups: Mapped[list["TagsGroup"]] = relationship(
        "TagsGroup", back_populates="general_account"
    )
    mistakes: Mapped[list["Mistake"]] = relationship(
        "Mistake", back_populates="general_account"
    )
    psychology_states: Mapped[list["PsychologyState"]] = relationship(
        "PsychologyState", back_populates="general_account"
    )
    news_impacts: Mapped[list["NewsImpact"]] = relationship(
        "NewsImpact", back_populates="general_account"
    )
    playbooks: Mapped[list["Playbook"]] = relationship(
        "Playbook", back_populates="general_account"
    )