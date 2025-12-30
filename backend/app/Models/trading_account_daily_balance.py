from sqlalchemy import Column, Numeric, Date, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.Infrastructure.db import Base
import uuid
from sqlalchemy import text

class TradingAccountDailyBalance(Base):
    __tablename__ = "trading_account_daily_balances"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trading_account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("trading_accounts.id"), nullable=False)
    balance_date: Mapped[Date] = mapped_column(Date, nullable=False)
    balance: Mapped[float] = mapped_column(Numeric, nullable=False, default=0)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
