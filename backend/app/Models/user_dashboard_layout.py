from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID as pgUUID, JSONB, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..Infrastructure.db import Base

class UserDashboardLayout(Base):
    __tablename__ = 'user_dashboard_layouts'
    __table_args__ = {'schema': 'public'}

    user_id: Mapped[uuid.UUID] = mapped_column(pgUUID(as_uuid=True), ForeignKey('auth.users.id'), primary_key=True)
    layout_config: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship to AuthUser
    user: Mapped["AuthUser"] = relationship("AuthUser", back_populates="dashboard_layout")

    def __repr__(self):
        return f"<UserDashboardLayout(user_id='{self.user_id}')>"
