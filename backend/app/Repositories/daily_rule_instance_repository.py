from typing import Sequence, Optional
from uuid import UUID
import datetime
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.Models.daily_rule_instance import DailyRuleInstance
from app.Models.note import Note
from app.Models.notebook_folder import NotebookFolder
from app.Repositories.base_repository import BaseRepository
from app.Schemas.discipline.daily_rule_instance import DailyRuleInstanceCreate, DailyRuleInstanceUpdate

class DailyRuleInstanceRepository(BaseRepository[DailyRuleInstance, DailyRuleInstanceCreate, DailyRuleInstanceUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(DailyRuleInstance, db)

    async def get_or_create(self, **kwargs) -> DailyRuleInstance:
        instance = await self.db.execute(
            select(self.model).filter_by(**kwargs)
        )
        instance = instance.scalars().first()

        if instance:
            return instance

        return await self.create(kwargs)

    async def find_by_note_and_trading_account(self, daily_note_id: UUID, trading_account_id: UUID) -> Sequence[DailyRuleInstance]:
        stmt = select(self.model).where(
            self.model.daily_journal_id == daily_note_id,
            self.model.trading_account_id == trading_account_id
        ).options(selectinload(self.model.rule_template))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def find_by_account_and_date_range(self, general_account_id: UUID, start_date: datetime.date, end_date: datetime.date) -> Sequence[tuple[DailyRuleInstance, datetime.date]]:
        stmt = (
            select(DailyRuleInstance, Note.note_date)
            .join(Note, DailyRuleInstance.daily_journal_id == Note.id)
            .join(NotebookFolder, Note.folder_id == NotebookFolder.id)
            .where(
                NotebookFolder.general_account_id == general_account_id,
                Note.note_date >= start_date,
                Note.note_date <= end_date
            )
        )
        result = await self.db.execute(stmt)
        return result.all()

    async def find_by_rule_and_date_range(self, rule_id: UUID, trading_account_id: UUID, date_range: list[date]) -> Sequence[DailyRuleInstance]:
        stmt = select(self.model).where(
            self.model.manual_rule_id == rule_id,
            self.model.trading_account_id == trading_account_id,
            self.model.date.in_(date_range)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()