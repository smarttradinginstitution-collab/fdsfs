import uuid
from sqlalchemy import Column, String, NUMERIC, DATE, ForeignKey, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.Infrastructure.db import Base

class OptionSymbol(Base):
    __tablename__ = 'option_symbols'

    id = Column(String, primary_key=True, index=True)
    description = Column(String, nullable=False)
    option_type = Column(String, nullable=False)
    strike_price = Column(NUMERIC, nullable=False)
    expiry_date = Column(DATE, nullable=False)
    underlying_symbol_id = Column(UUID(as_uuid=True), ForeignKey('securities.id'), nullable=False)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    underlying_symbol = relationship("Security")

    def __repr__(self):
        return f"<OptionSymbol(id='{self.id}', description='{self.description}')>"
