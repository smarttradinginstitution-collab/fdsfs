# app/Schemas/rules_group_playbook.py
from __future__ import annotations
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

# Forward reference per RuleRead, che verrà definito in un altro file.
# from app.Schemas.rule_playbook import RuleRead

# Schema di base con i campi comuni
class RulesGroupBase(BaseModel):
    name_group: Optional[str] = Field(None, description="The name of the rule group")

    class Config:
        from_attributes = True

# Schema per la creazione di un gruppo (usato nel body delle richieste POST)
class RulesGroupCreate(RulesGroupBase):
    name_group: str = Field(..., description="The name of the group is required")
    playbook_id: UUID = Field(..., description="The ID of the parent playbook")

# Schema per l'aggiornamento di un gruppo (usato nel body delle richieste PUT/PATCH)
class RulesGroupUpdate(RulesGroupBase):
    pass # name_group è già opzionale in RulesGroupBase

# Schema per la lettura di un gruppo (usato nelle risposte GET)
# Questo includerà le regole associate.
class RulesGroupRead(RulesGroupBase):
    id: UUID
    playbook_id: UUID
    name_group: str
    created_at: datetime
    rules: List["RuleRead"] = []

# Necessario per aggiornare i forward reference dopo che tutti i modelli sono stati caricati.
# FastAPI di solito lo gestisce automaticamente.
# RulesGroupRead.model_rebuild()