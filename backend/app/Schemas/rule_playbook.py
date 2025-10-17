# app/Schemas/rule_playbook.py
from __future__ import annotations
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class RuleMetrics(BaseModel):
    follow_rate: float
    net_pnl: float
    profit_factor: Optional[float]
    win_rate: float

class RuleBase(BaseModel):
    rule: Optional[str] = Field(None, description="The content of the rule")
    model_config = {"from_attributes": True}

class RuleCreate(RuleBase):
    rule: str = Field(..., description="The content of the rule is required")
    rules_groups_playbook_id: UUID = Field(..., description="The ID of the parent rule group")

class RuleUpdate(RuleBase):
    pass

class RuleReorder(BaseModel):
    rule_ids: List[UUID] = Field(..., description="An ordered list of rule IDs.")

# This class now comes AFTER RuleMetrics
class RuleRead(RuleBase):
    id: UUID
    rules_groups_playbook_id: UUID
    rule: str
    order: Optional[int] = None
    created_at: datetime
    metrics: Optional[RuleMetrics] = None