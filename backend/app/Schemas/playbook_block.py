
# app/Schemas/playbook_block.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID

class PlaybookBlockBase(BaseModel):
    title: Optional[str] = Field(None, description="The custom title of the block")
    content: Optional[Dict[str, Any]] = Field(None, description="The JSON content of the block, containing groups and items")

class PlaybookBlockCreate(PlaybookBlockBase):
    title: str = Field(..., description="Title is required for new blocks")

class PlaybookBlockUpdate(PlaybookBlockBase):
    pass

class PlaybookBlockRead(PlaybookBlockBase):
    id: UUID
    title: str
    content: Dict[str, Any]

    model_config = {"from_attributes": True}
