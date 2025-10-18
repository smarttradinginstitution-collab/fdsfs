import uuid
import datetime
from pydantic import BaseModel, Field
from typing import List

class ManualRuleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name of the manual rule.")
    frequency: List[int] = Field(..., description="Days of the week the rule is active, e.g., [1,2,3,4,5]")

class ManualRuleCreate(ManualRuleBase):
    pass

class ManualRuleUpdate(ManualRuleBase):
    pass

class ManualRuleRead(ManualRuleBase):
    id: uuid.UUID
    general_account_id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True