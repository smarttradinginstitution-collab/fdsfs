# app/Schemas/playbook_condition.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID

class PlaybookConditionBase(BaseModel):
    category: str
    variable: str
    operator: str
    value: Dict[str, Any]
    order: Optional[int] = None

class PlaybookConditionCreate(PlaybookConditionBase):
    playbook_id: UUID

class PlaybookConditionUpdate(PlaybookConditionBase):
    pass

class PlaybookConditionRead(PlaybookConditionBase):
    id: UUID

    class Config:
        orm_mode = True
