from typing import Sequence, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.Models.discipline_rule import DisciplineRule

class DisciplineRuleRepository:
    """
    Repository for the `discipline_rules` table.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> DisciplineRule:
        """
        Creates a new discipline rule.
        """
        rule = DisciplineRule(**data)
        self.db.add(rule)
        await self.db.commit()
        await self.db.refresh(rule)
        return rule

    async def get_by_id(self, rule_id: UUID) -> Optional[DisciplineRule]:
        """
        Gets a discipline rule by its ID.
        """
        return await self.db.get(DisciplineRule, rule_id)

    async def list_by_general_account(self, general_account_id: UUID) -> Sequence[DisciplineRule]:
        """
        Lists all discipline rules for a given general account.
        """
        stmt = select(DisciplineRule).where(DisciplineRule.general_account_id == general_account_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update(self, rule_id: UUID, data: dict) -> Optional[DisciplineRule]:
        """
        Updates a discipline rule.
        """
        rule = await self.get_by_id(rule_id)
        if rule:
            for key, value in data.items():
                if value is not None:
                    setattr(rule, key, value)
            await self.db.commit()
            await self.db.refresh(rule)
        return rule

    async def delete(self, rule_id: UUID) -> bool:
        """
        Deletes a discipline rule.
        """
        rule = await self.get_by_id(rule_id)
        if rule:
            await self.db.delete(rule)
            await self.db.commit()
            return True
        return False