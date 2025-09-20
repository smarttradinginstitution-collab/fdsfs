from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class BrokerageSchema(BaseModel):
    id: UUID
    name: str
    display_name: Optional[str] = None
    aws_s3_logo_url: Optional[str] = None

    class Config:
        from_attributes = True

class ConnectionSchema(BaseModel):
    id: UUID
    created_date: datetime
    brokerage: BrokerageSchema
    name: str
    type: str
    disabled: bool
    disabled_date: Optional[datetime] = None
    # meta is deprecated
    # updated_date is deprecated
    is_eligible_for_payout: bool

    class Config:
        from_attributes = True
