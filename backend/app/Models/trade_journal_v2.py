from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID, BIGINT
from sqlalchemy.orm import Mapped, mapped_column
from app.Infrastructure.db import Base
from sqlalchemy import text

class TradeJournalV2(Base):
    __tablename__ = "TradeJournalV2"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, server_default=text("GENERATED ALWAYS AS IDENTITY"))
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
