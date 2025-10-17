# backend/app/Controllers/discipline_controller.py
from __future__ import annotations

from typing import List
from uuid import UUID

from app.Services.discipline_service import DisciplineService
from app.Schemas.discipline_rule import (
    DisciplineRuleRead,
    DisciplineRuleCreate,
    DisciplineRuleUpdate,
)
from app.Schemas.journal import ProgressTrackerSummary


class DisciplineController:
    async def get_all_rules(
        self,
        claims: dict,
        service: DisciplineService,
    ) -> List[DisciplineRuleRead]:
        return await service.get_all_rules(claims)

    async def create_rule(
        self,
        claims: dict,
        rule_create: DisciplineRuleCreate,
        service: DisciplineService,
    ) -> DisciplineRuleRead:
        return await service.create_rule(claims, rule_create)

    async def update_rule(
        self,
        claims: dict,
        rule_id: UUID,
        rule_update: DisciplineRuleUpdate,
        service: DisciplineService,
    ) -> DisciplineRuleRead:
        return await service.update_rule(claims, rule_id, rule_update)

    async def delete_rule(
        self,
        claims: dict,
        rule_id: UUID,
        service: DisciplineService,
    ) -> None:
        await service.delete_rule(claims, rule_id)
        return None

    async def get_progress_tracker_summary(
        self,
        claims: dict,
        service: DisciplineService,
    ) -> ProgressTrackerSummary:
        return await service.get_progress_tracker_summary(claims)