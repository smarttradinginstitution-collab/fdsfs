# app/Schemas/playbook.py
from __future__ import annotations
from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

# Schema di base con i campi comuni
class PlaybookBase(BaseModel):
    title: Optional[str] = Field(None, description="The title of the playbook")

    class Config:
        from_attributes = True

# Schema per la creazione di un playbook (usato nel body delle richieste POST)
class PlaybookCreate(PlaybookBase):
    title: str = Field(..., description="The title of the playbook is required for creation")

# Schema per l'aggiornamento di un playbook (usato nel body delle richieste PUT/PATCH)
class PlaybookUpdate(PlaybookBase):
    pass # title è già opzionale in PlaybookBase

# Schema per la lettura di un playbook (usato nelle risposte GET)
class PlaybookRead(PlaybookBase):
    id: UUID
    general_account_id: UUID
    created_at: datetime