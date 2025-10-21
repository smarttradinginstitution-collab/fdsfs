# backend/app/Schemas/pagination.py
from typing import Generic, TypeVar, List
from pydantic import BaseModel

DataType = TypeVar('DataType')

class PaginatedResponse(BaseModel, Generic[DataType]):
    total: int
    items: List[DataType]
