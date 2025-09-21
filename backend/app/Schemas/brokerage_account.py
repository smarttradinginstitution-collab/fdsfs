# app/Schemas/brokerage_account.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, Any, List
import uuid
from datetime import datetime

# This schema is used for individual account items in a list
class BrokerageAccountInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    connection_id: uuid.UUID
    name: str
    number: str
    balance: float
    currency: Optional[str] = None
    institution_name: str
    created_at: datetime
    updated_at: datetime
    status: Optional[str] = None
    sync_status: Optional[dict[str, Any]] = None

# This is the response model for the GET /accounts endpoint
class AccountListResponse(BaseModel):
    accounts: List[BrokerageAccountInfo]
    warning: Optional[dict[str, Any]] = None

# This schema is for updating account details in the repository
class BrokerageAccountUpdate(BaseModel):
    name: Optional[str] = None
    number: Optional[str] = None
    status: Optional[str] = None
    sync_status: Optional[dict[str, Any]] = None
