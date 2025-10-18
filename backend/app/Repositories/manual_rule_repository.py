from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from app.Models.manual_rule import ManualRule
from app.Repositories.base_repository import BaseRepository

class ManualRuleRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, ManualRule)

    async def list_by_general_account(self, general_account_id: UUID) -> list[ManualRule]:
        result = await self.db.execute(
            select(self.model)
            .filter_by(general_account_id=general_account_id)
            .order_by(self.model.created_at)
        )
        return result.scalars().all()