# app/Schemas/broker.py
from __future__ import annotations
from uuid import UUID
from pydantic import BaseModel


class BrokerBase(BaseModel):
    name: str


class BrokerCreate(BrokerBase):
    pass


class BrokerUpdate(BrokerBase):
    pass


class BrokerRead(BrokerBase):
    id: UUID

    model_config = {"from_attributes": True}