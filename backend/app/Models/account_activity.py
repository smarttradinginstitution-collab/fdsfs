import uuid
from sqlalchemy import Column, String, NUMERIC, TIMESTAMP, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.Infrastructure.db import Base

class AccountActivity(Base):
    __tablename__ = 'account_activities'

    id = Column(String, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey('brokerage_accounts.id', ondelete='CASCADE'), nullable=False)
    security_id = Column(UUID(as_uuid=True), ForeignKey('securities.id', ondelete='CASCADE'), nullable=True)
    option_symbol_id = Column(String, ForeignKey('option_symbols.id', ondelete='CASCADE'), nullable=True)

    type = Column(String, nullable=False, index=True)
    option_type = Column(String, nullable=True)
    price = Column(NUMERIC, nullable=True)
    units = Column(NUMERIC, nullable=True)
    amount = Column(NUMERIC, nullable=True)
    description = Column(String, nullable=True)
    trade_date = Column(TIMESTAMP(timezone=True), nullable=True)
    settlement_date = Column(TIMESTAMP(timezone=True), nullable=True)
    fee = Column(NUMERIC, nullable=True)
    fx_rate = Column(NUMERIC, nullable=True)
    institution = Column(String, nullable=True)
    external_reference_id = Column(String, nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("Profile")
    account = relationship("BrokerageAccount")
    security = relationship("Security")
    option_symbol = relationship("OptionSymbol")

    def __repr__(self):
        return f"<AccountActivity(id='{self.id}', type='{self.type}', account_id='{self.account_id}')>"
