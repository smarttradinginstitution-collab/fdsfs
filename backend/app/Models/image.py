from __future__ import annotations
import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.Infrastructure.db import Base
from sqlalchemy.dialects.postgresql import UUID

if TYPE_CHECKING:
    from app.Models.general_account import GeneralAccount

class Image(Base):
    __tablename__ = "images"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    general_account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("public.general_accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    filename: Mapped[str] = mapped_column(nullable=False)
    file_path: Mapped[str] = mapped_column(nullable=False, unique=True)
    url: Mapped[str] = mapped_column(nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # --- Relationships ---
    general_account: Mapped["GeneralAccount"] = relationship(back_populates="images")