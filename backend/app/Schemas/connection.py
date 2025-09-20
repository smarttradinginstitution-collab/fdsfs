from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class ConnectionSchema(BaseModel):
    id: UUID
    user_id: UUID
    brokerage_name: str
    brokerage_display_name: Optional[str] = None
    brokerage_logo_url: Optional[str] = None
    connection_type: str
    disabled: bool
    disabled_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
