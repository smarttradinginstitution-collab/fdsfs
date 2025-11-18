
# app/Schemas/playbook_block.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID
from app.Models.enums import PlaybookBlockType

class PlaybookBlockBase(BaseModel):
    block_type: PlaybookBlockType = Field(PlaybookBlockType.CONDITIONS, description="The type of the block")
    title: Optional[str] = Field(None, description="The custom title of the block")
    content: Optional[Dict[str, Any]] = Field(None, description="The JSON content of the block")

class PlaybookBlockCreate(PlaybookBlockBase):
    block_type: PlaybookBlockType
    title: str = Field(..., description="Title is required for new blocks")

class PlaybookBlockUpdate(PlaybookBlockBase):
    pass

class PlaybookBlockRead(PlaybookBlockBase):
    id: UUID
    block_type: PlaybookBlockType
    title: str
    content: Dict[str, Any]

    model_config = {"from_attributes": True}
