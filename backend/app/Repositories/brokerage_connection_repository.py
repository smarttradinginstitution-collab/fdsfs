# app/Repositories/brokerage_connection_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.Models.brokerage_connection import BrokerageConnection
import uuid

class BrokerageConnectionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_by_user(self, user_id: uuid.UUID) -> list[BrokerageConnection]:
        result = await self.db.execute(
            select(BrokerageConnection).where(BrokerageConnection.user_id == user_id)
        )
        return result.scalars().all()
