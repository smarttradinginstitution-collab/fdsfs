# app/Models/profile.py

from __future__ import annotations
import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.Infrastructure.db import Base

class Profile(Base):
    __tablename__ = "profiles"
    __table_args__ = {"schema": "public", "extend_existing": True}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("auth.users.id"), primary_key=True)
    snaptrade_user_secret: Mapped[str | None] = mapped_column(String)

    # Relationship to AuthUser (one-to-one)
    user: Mapped["AuthUser"] = relationship(back_populates="profile")

    @property
    def has_snaptrade_user_secret(self) -> bool:
        """Computed property to safely expose the presence of a secret."""
        return self.snaptrade_user_secret is not None
