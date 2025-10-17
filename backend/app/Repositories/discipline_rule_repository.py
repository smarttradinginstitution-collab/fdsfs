# backend/app/Repositories/discipline_rule_repository.py
from __future__ import annotations

from uuid import UUID
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.discipline_rule import DisciplineRule
from app.Schemas.discipline_rule import DisciplineRuleCreate, DisciplineRuleUpdate


class DisciplineRuleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self, rule_id: UUID, general_account_id: UUID
    ) -> Optional[DisciplineRule]:
        query = select(DisciplineRule).where(
            DisciplineRule.id == rule_id,
            DisciplineRule.general_account_id == general_account_id,
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def list_by_general_account_id(
        self, general_account_id: UUID
    ) -> List[DisciplineRule]:
        query = select(DisciplineRule).where(
            DisciplineRule.general_account_id == general_account_id
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(
        self, rule_create: DisciplineRuleCreate, general_account_id: UUID
    ) -> DisciplineRule:
        db_rule = DisciplineRule(
            **rule_create.model_dump(), general_account_id=general_account_id
        )
        self.db.add(db_rule)
        await self.db.commit()
        await self.db.refresh(db_rule)
        return db_rule

    async def update(
        self, db_rule: DisciplineRule, rule_update: DisciplineRuleUpdate
    ) -> DisciplineRule:
        for key, value in rule_update.model_dump(exclude_unset=True).items():
            setattr(db_rule, key, value)
        await self.db.commit()
        await self.db.refresh(db_rule)
        return db_rule

    async def delete(self, db_rule: DisciplineRule) -> None:
        await self.db.delete(db_rule)
        await self.db.commit()