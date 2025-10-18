import uuid
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DailyRuleInstanceBase(BaseModel):
    name: str
    rule_type: str
    status: str
    actual_value: Optional[str] = None

class DailyRuleInstanceUpdate(BaseModel):
    status: Optional[str] = Field(None, description="New status: 'completed', 'failed'")
    actual_value: Optional[str] = Field(None, description="The actual value for the rule, e.g., '$500 / $4000'")

class DailyRuleInstanceRead(DailyRuleInstanceBase):
    id: uuid.UUID
    daily_journal_id: uuid.UUID
    rule_template_id: Optional[uuid.UUID]
    created_at: datetime

    class Config:
        from_attributes = True