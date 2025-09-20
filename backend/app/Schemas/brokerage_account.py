import uuid
import datetime
from pydantic import BaseModel, ConfigDict

class BrokerageAccountRead(BaseModel):
    id: uuid.UUID
    connection_id: uuid.UUID
    name: str
    number: str
    balance: float
    currency: str | None
    institution_name: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class AccountListResponse(BaseModel):
    accounts: list[BrokerageAccountRead]
    warning: dict | None = None
