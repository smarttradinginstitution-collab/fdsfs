# app/Schemas/trades_playbooks.py

from __future__ import annotations

from uuid import UUID
from pydantic import BaseModel


class TradesPlaybooksCreate(BaseModel):
    trade_id: UUID
    playbook_id: UUID


class TradesPlaybooksDelete(BaseModel):
    trade_id: UUID
    playbook_id: UUID


class TradesPlaybooksRead(BaseModel):
    trade_id: UUID
    playbook_id: UUID
    user_id: UUID

    class Config:
        from_attributes = True