# app/Models/profile.py

from __future__ import annotations
import uuid
import datetime
from typing import List
from sqlalchemy import String, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.Infrastructure.db import Base
from app.Models.brokerage_connection import BrokerageConnection
from app.Models.brokerage_account import BrokerageAccount

class Profile(Base):
    __tablename__ = "profiles"
    __table_args__ = {"schema": "public", "extend_existing": True}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("auth.users.id"), primary_key=True)
    snaptrade_user_secret: Mapped[str | None] = mapped_column(String)
    last_synced_at: Mapped[datetime.datetime | None] = mapped_column(TIMESTAMP(timezone=True))

    # Relationship to AuthUser (one-to-one)
    user: Mapped["AuthUser"] = relationship(back_populates="profile")

    # Relationship to BrokerageConnection (one-to-many)
    brokerage_connections: Mapped[List["BrokerageConnection"]] = relationship(back_populates="profile")

    # Relationship to BrokerageAccount (one-to-many)
    brokerage_accounts: Mapped[List["BrokerageAccount"]] = relationship(back_populates="profile")

    @property
    def has_snaptrade_user_secret(self) -> bool:
        """Computed property to safely expose the presence of a secret."""
        return self.snaptrade_user_secret is not None
