# app/Schemas/broker.py
from __future__ import annotations
from uuid import UUID
from pydantic import BaseModel


class BrokerRead(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True