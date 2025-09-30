# app/Schemas/rule_playbook.py
from __future__ import annotations
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

# Schema di base con i campi comuni
class RuleBase(BaseModel):
    rule: Optional[str] = Field(None, description="The content of the rule")

    class Config:
        from_attributes = True

# Schema per la creazione di una regola (usato nel body delle richieste POST)
class RuleCreate(RuleBase):
    rule: str = Field(..., description="The content of the rule is required")
    rules_groups_playbook_id: UUID = Field(..., description="The ID of the parent rule group")

# Schema per l'aggiornamento di una regola (usato nel body delle richieste PUT/PATCH)
class RuleUpdate(RuleBase):
    pass # rule è già opzionale in RuleBase


# Schema for reordering rules within a group
class RuleReorder(BaseModel):
    rule_ids: List[UUID] = Field(..., description="An ordered list of rule IDs.")


# Schema for rule performance metrics
class RuleMetrics(BaseModel):
    follow_rate: float
    net_pnl: float
    profit_factor: Optional[float]  # Can be None if gross_loss is 0
    win_rate: float


# Schema per la lettura di una regola (usato nelle risposte GET)
class RuleRead(RuleBase):
    id: UUID
    rules_groups_playbook_id: UUID
    rule: str
    order: Optional[int] = None
    created_at: datetime
    metrics: Optional[RuleMetrics] = None