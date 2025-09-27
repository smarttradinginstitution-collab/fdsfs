# app/Repositories/broker_repository.py
from __future__ import annotations

from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.broker import Broker


class BrokerRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_all(self) -> List[Broker]:
        """Lists all brokers."""
        stmt = select(Broker).order_by(Broker.name)
        result = await self.db.execute(stmt)
        return result.scalars().all()