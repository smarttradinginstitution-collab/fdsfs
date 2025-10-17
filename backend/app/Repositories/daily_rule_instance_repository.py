# backend/app/Repositories/daily_rule_instance_repository.py
from __future__ import annotations

from uuid import UUID
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.daily_rule_instance import DailyRuleInstance


class DailyRuleInstanceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_by_journal_id(
        self, daily_journal_id: UUID
    ) -> List[DailyRuleInstance]:
        query = select(DailyRuleInstance).where(
            DailyRuleInstance.daily_journal_id == daily_journal_id
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_many(self, instances_data: List[dict]) -> List[DailyRuleInstance]:
        instances = [DailyRuleInstance(**data) for data in instances_data]
        self.db.add_all(instances)
        await self.db.commit()
        # Note: Refreshing is not straightforward with add_all.
        # The service layer will need to re-fetch if updated instances are needed.
        return instances

    async def get_by_id(self, instance_id: UUID) -> DailyRuleInstance | None:
        return await self.db.get(DailyRuleInstance, instance_id)

    async def commit_and_refresh(self, instance: DailyRuleInstance) -> DailyRuleInstance:
        await self.db.commit()
        await self.db.refresh(instance)
        return instance