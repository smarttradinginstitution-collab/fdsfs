# app/Services/broker_service.py
from __future__ import annotations

from typing import List
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Repositories.broker_repository import BrokerRepository
from app.Models.broker import Broker


class BrokerService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.repo = BrokerRepository(db)

    async def get_all_brokers(self) -> List[Broker]:
        """Returns a list of all brokers."""
        return await self.repo.list_all()