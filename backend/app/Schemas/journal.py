# backend/app/Schemas/journal.py
from __future__ import annotations

from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from datetime import date

from app.Schemas.daily_rule_instance import DailyRuleInstanceRead
from app.Schemas.notebook import NoteRead


class JournalDay(BaseModel):
    note: NoteRead
    rules: List[DailyRuleInstanceRead]
    pnl: float

    model_config = ConfigDict(from_attributes=True)


class ProgressTrackerSummary(BaseModel):
    score_history: dict[date, float]
    streak: int
    follow_rate: dict[str, float]

    model_config = ConfigDict(from_attributes=True)