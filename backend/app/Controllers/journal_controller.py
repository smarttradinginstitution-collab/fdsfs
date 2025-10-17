# backend/app/Controllers/journal_controller.py
from __future__ import annotations

from typing import List
from uuid import UUID
from datetime import date

from fastapi import Body, Depends
from app.Services.journal_service import JournalService
from app.Router.auth import get_current_claims
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
        instance_id: UUID,
        status: str = Body(..., embed=True),
        claims: dict = Depends(get_current_claims),
        service: JournalService = Depends(),
    ) -> DailyRuleInstanceRead:
        return await service.update_manual_rule_status(claims, instance_id, status)