# app/Models/user_dashboard_layout.py
# Modello SQLAlchemy per la tabella public.user_dashboard_layouts

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import TIMESTAMP, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.Infrastructure.db import Base


class UserDashboardLayout(Base):
    __tablename__ = "user_dashboard_layouts"
    __table_args__ = (
        {"schema": "public"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    layout: Mapped[dict | list] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
