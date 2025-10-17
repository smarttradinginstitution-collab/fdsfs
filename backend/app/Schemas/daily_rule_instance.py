# backend/app/Schemas/daily_rule_instance.py
from __future__ import annotations

from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class DailyRuleInstanceBase(BaseModel):
    name: str
    rule_type: str
    status: str
    actual_value: Optional[str] = None


class DailyRuleInstanceRead(DailyRuleInstanceBase):
    id: UUID
    rule_template_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)