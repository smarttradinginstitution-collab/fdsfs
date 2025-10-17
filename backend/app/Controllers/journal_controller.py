# backend/app/Controllers/journal_controller.py
from __future__ import annotations

from typing import List
from uuid import UUID
from datetime import date

from fastapi import Body
from app.Services.journal_service import JournalService
from app.Schemas.journal import JournalDay
from app.Schemas.daily_rule_instance import DailyRuleInstanceRead


class JournalController:
    async def start_day(
        self,
        claims: dict,
        day: date,
        service: JournalService,
    ) -> JournalDay:
        return await service.start_day(claims, day)

    async def get_day(
        self,
        claims: dict,
        day: date,
        service: JournalService,
    ) -> JournalDay:
        return await service.get_day(claims, day)

    async def update_manual_rule(
        self,
        claims: dict,
        instance_id: UUID,
        service: JournalService,
        status: str = Body(..., embed=True),
    ) -> DailyRuleInstanceRead:
        return await service.update_manual_rule_status(claims, instance_id, status)