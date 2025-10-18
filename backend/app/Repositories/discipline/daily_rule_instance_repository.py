from typing import Sequence, Optional
from uuid import UUID
import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.Models.daily_rule_instance import DailyRuleInstance
from app.Models.note import Note

class DailyRuleInstanceRepository:
    """
    Repository for the `daily_rule_instances` table.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_many(self, instances_data: list[dict]) -> Sequence[DailyRuleInstance]:
        """
        Creates multiple daily rule instances from a list of data.
        """
        instances = [DailyRuleInstance(**data) for data in instances_data]
        self.db.add_all(instances)
        await self.db.commit()
        # No refresh on bulk insert, caller handles what to return
        return instances

    async def get_by_id(self, instance_id: UUID) -> Optional[DailyRuleInstance]:
        """
        Gets a daily rule instance by its ID.
        """
        return await self.db.get(DailyRuleInstance, instance_id)

    async def find_by_journal_and_date(self, daily_journal_id: UUID) -> Sequence[DailyRuleInstance]:
        """
        Finds all daily rule instances for a specific journal entry.
        """
        stmt = select(DailyRuleInstance).where(DailyRuleInstance.daily_journal_id == daily_journal_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def find_by_account_and_date_range(self, general_account_id: UUID, start_date: datetime.date, end_date: datetime.date) -> Sequence[tuple[DailyRuleInstance, datetime.date]]:
        """
        Finds all daily rule instances for a general account within a date range,
        returning both the instance and the note's date to avoid N+1 queries.
        """
        stmt = (
            select(DailyRuleInstance, Note.note_date)
            .join(Note, DailyRuleInstance.daily_journal_id == Note.id)
            .where(
                Note.general_account_id == general_account_id,
                Note.note_date >= start_date,
                Note.note_date <= end_date
            )
        )
        result = await self.db.execute(stmt)
        return result.all()

    async def update(self, instance_id: UUID, data: dict) -> Optional[DailyRuleInstance]:
        """
        Updates a daily rule instance.
        """
        instance = await self.get_by_id(instance_id)
        if instance:
            for key, value in data.items():
                if value is not None:
                    setattr(instance, key, value)
            await self.db.commit()
            await self.db.refresh(instance)
        return instance