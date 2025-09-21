from pydantic import BaseModel, ConfigDict
from typing import Optional
import uuid

class SecurityBase(BaseModel):
    id: uuid.UUID
    symbol: str
    description: Optional[str] = None
    currency_code: Optional[str] = None
    exchange_name: Optional[str] = None
    figi_code: Optional[str] = None

class SecurityCreate(SecurityBase):
    pass

class SecurityRead(SecurityBase):
    model_config = ConfigDict(from_attributes=True)
