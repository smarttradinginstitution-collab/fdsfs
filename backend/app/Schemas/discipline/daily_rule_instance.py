import uuid
import datetime
from pydantic import BaseModel, Field
from typing import Optional

class DailyRuleInstanceBase(BaseModel):
    status: str = Field(..., description="Status of the rule instance")

class DailyRuleInstanceCreate(BaseModel):
    manual_rule_id: uuid.UUID
    trading_account_id: uuid.UUID
    daily_journal_id: uuid.UUID
    date: datetime.date
    status: Optional[str] = 'pending'


class DailyRuleInstanceUpdate(DailyRuleInstanceBase):
    pass

class DailyRuleInstanceRead(DailyRuleInstanceBase):
    id: uuid.UUID
    manual_rule_id: uuid.UUID
    trading_account_id: uuid.UUID
    daily_journal_id: uuid.UUID
    date: datetime.date
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True