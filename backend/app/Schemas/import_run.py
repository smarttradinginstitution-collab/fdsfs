# backend/app/Schemas/import_run.py
import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.Models.enums import ImportSourceType

class ImportRunBase(BaseModel):
    source_type: ImportSourceType
    file_name: Optional[str] = None
    status: str
    total_rows: int = 0
    inserted_count: int = 0
    updated_count: int = 0
    skipped_count: int = 0
    error_message: Optional[str] = None

class ImportRunCreate(ImportRunBase):
    user_id: uuid.UUID
    trading_account_id: uuid.UUID

class ImportRunRead(ImportRunBase):
    id: uuid.UUID
    user_id: uuid.UUID
    trading_account_id: uuid.UUID
    created_at: datetime
    finished_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)