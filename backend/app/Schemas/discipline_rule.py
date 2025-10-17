# backend/app/Schemas/discipline_rule.py
from __future__ import annotations

from typing import Optional, List, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class DisciplineRuleBase(BaseModel):
    rule_type: str
    name: str
    description: Optional[str] = None
    condition_type: Optional[str] = None
    condition_value: Optional[dict] = None
    active_days: List[int]


class DisciplineRuleCreate(DisciplineRuleBase):
    pass


class DisciplineRuleUpdate(DisciplineRuleBase):
    pass


class DisciplineRuleRead(DisciplineRuleBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)