from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from app.Models.discipline_settings import DisciplineSettings
from app.Repositories.base_repository import BaseRepository

class DisciplineSettingsRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, DisciplineSettings)

    async def get_by_general_account_id(self, general_account_id: UUID) -> DisciplineSettings | None:
        result = await self.db.execute(
            select(self.model).filter_by(general_account_id=general_account_id)
        )
        return result.scalars().first()