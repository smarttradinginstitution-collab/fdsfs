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

# Schema per la lettura di una regola (usato nelle risposte GET)
class RuleRead(RuleBase):
    id: UUID
    rules_groups_playbook_id: UUID
    rule: str
    created_at: datetime


# Schema for updating the rules associated with a trade
class TradeRulesUpdate(BaseModel):
    rule_ids: List[UUID] = Field(..., description="A list of rule IDs to associate with the trade")