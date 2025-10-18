import uuid
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class DisciplineRuleBase(BaseModel):
    rule_type: str = Field(..., description="Type of the rule: 'AUTOMATED' or 'MANUAL'")
    name: str = Field(..., description="Name of the rule")
    description: Optional[str] = None
    condition_type: Optional[str] = Field(None, description="Type of condition: 'TIME', 'PERCENTAGE', 'FIXED_AMOUNT', etc.")
    condition_value: Optional[Dict[str, Any]] = Field(None, description="Value of the condition, e.g., {'time': '12:00'}")
    active_days: List[int] = Field(..., description="Days of the week the rule is active, e.g., [1,2,3,4,5]")

class DisciplineRuleCreate(DisciplineRuleBase):
    pass

class DisciplineRuleUpdate(BaseModel):
    rule_type: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    condition_type: Optional[str] = None
    condition_value: Optional[Dict[str, Any]] = None
    active_days: Optional[List[int]] = None

class DisciplineRuleRead(DisciplineRuleBase):
    id: uuid.UUID
    general_account_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True