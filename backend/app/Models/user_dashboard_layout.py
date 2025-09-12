# app/Models/user_dashboard_layout.py

from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy import (
    ForeignKey,
    DateTime,
    func
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.Infrastructure.db import Base

__all__ = ["UserDashboardLayout"]

class UserDashboardLayout(Base):
    """
    Represents the layout of a user's dashboard.
    """
    __tablename__ = "user_dashboard_layouts"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # Ensure one layout per user
    )
    layout: Mapped[dict | list] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
