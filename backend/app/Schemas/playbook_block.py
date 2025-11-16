# app/Schemas/playbook_block.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID
from app.Models.enums import PlaybookBlockType

class PlaybookBlockBase(BaseModel):
    block_type: PlaybookBlockType
    content: Optional[Dict[str, Any]] = None
    order: Optional[int] = None

class PlaybookBlockCreate(PlaybookBlockBase):
    playbook_id: UUID

class PlaybookBlockUpdate(PlaybookBlockBase):
    pass

class PlaybookBlockRead(PlaybookBlockBase):
    id: UUID

    model_config = {"from_attributes": True}
