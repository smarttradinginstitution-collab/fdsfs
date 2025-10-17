# backend/app/Services/discipline_service.py
from __future__ import annotations

from uuid import UUID
from typing import List
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Repositories.discipline_rule_repository import DisciplineRuleRepository
from app.Schemas.discipline_rule import (
    DisciplineRuleCreate,
    DisciplineRuleUpdate,
    DisciplineRuleRead,
)
from app.Repositories.general_account_repository import GeneralAccountRepository
from app.Models.discipline_rule import DisciplineRule
from app.Schemas.journal import ProgressTrackerSummary
from datetime import date, timedelta


class DisciplineService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
        self.repo = DisciplineRuleRepository(db)
        self.general_account_repo = GeneralAccountRepository(db)

    async def _get_general_account_id(self, user_id: UUID) -> UUID:
        general_account = await self.general_account_repo.get_by_user_id(user_id)
        if not general_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="General Account not found.",
            )
        return general_account.id

    async def get_all_rules(self, claims: dict) -> List[DisciplineRuleRead]:
        user_id = UUID(claims["sub"])
        general_account_id = await self._get_general_account_id(user_id)
        rules = await self.repo.list_by_general_account_id(general_account_id)
        return [DisciplineRuleRead.model_validate(rule) for rule in rules]

    async def create_rule(
        self, claims: dict, rule_create: DisciplineRuleCreate
    ) -> DisciplineRuleRead:
        user_id = UUID(claims["sub"])
        general_account_id = await self._get_general_account_id(user_id)
        rule = await self.repo.create(rule_create, general_account_id)
        return DisciplineRuleRead.model_validate(rule)

    async def update_rule(
        self, claims: dict, rule_id: UUID, rule_update: DisciplineRuleUpdate
    ) -> DisciplineRuleRead:
        user_id = UUID(claims["sub"])
        general_account_id = await self._get_general_account_id(user_id)
        db_rule = await self.repo.get_by_id(rule_id, general_account_id)
        if not db_rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found"
            )
        rule = await self.repo.update(db_rule, rule_update)
        return DisciplineRuleRead.model_validate(rule)

    async def delete_rule(self, claims: dict, rule_id: UUID) -> None:
        user_id = UUID(claims["sub"])
        general_account_id = await self._get_general_account_id(user_id)
        db_rule = await self.repo.get_by_id(rule_id, general_account_id)
        if not db_rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found"
            )
        await self.repo.delete(db_rule)

    async def get_progress_tracker_summary(
        self, claims: dict
    ) -> ProgressTrackerSummary:
        user_id = UUID(claims["sub"])
        general_account_id = await self._get_general_account_id(user_id)

        # This is a simplified implementation. A real implementation would involve
        # more complex queries and logic to calculate the streak and score history.
        rule_stats = await self.repo.get_rule_statistics(general_account_id)
        follow_rate = {
            stat.name: (stat.completed_instances / stat.total_instances) * 100
            if stat.total_instances > 0
            else 0
            for stat in rule_stats
        }

        return ProgressTrackerSummary(
            score_history={},
            streak=0,
            follow_rate=follow_rate,
        )