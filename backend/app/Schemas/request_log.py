# app/Schemas/request_log.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from typing import List

class RequestLogRead(BaseModel):
    id: UUID
    method: str
    path: str
    status_code: int
    response_time_ms: int
    created_at: datetime

    class Config:
        from_attributes = True

class PaginatedRequestLogResponse(BaseModel):
    total: int
    data: List[RequestLogRead]