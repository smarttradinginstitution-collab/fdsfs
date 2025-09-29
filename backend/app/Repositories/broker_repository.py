# app/Repositories/broker_repository.py
from __future__ import annotations

import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.Models.broker import Broker


class BrokerRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> Broker:
        """Creates a new broker."""
        broker = Broker(**data)
        self.db.add(broker)
        await self.db.commit()
        await self.db.refresh(broker)
        return broker

    async def get_by_id(self, broker_id: uuid.UUID) -> Broker | None:
        """Gets a broker by its ID."""
        stmt = select(Broker).where(Broker.id == broker_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_by_id_with_relationships(self, broker_id: uuid.UUID) -> Broker | None:
        """
        Gets a broker by its ID with its relationships loaded
        for checking if it's in use.
        """
        stmt = (
            select(Broker)
            .where(Broker.id == broker_id)
            .options(
                selectinload(Broker.trading_accounts),
                selectinload(Broker.platforms),
                selectinload(Broker.asset_aliases),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_by_name(self, name: str) -> Broker | None:
        """Gets a broker by its name to check for duplicates."""
        stmt = select(Broker).where(Broker.name == name)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_all(self) -> List[Broker]:
        """Lists all brokers."""
        stmt = select(Broker).order_by(Broker.name)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update(self, broker: Broker, data: dict) -> Broker:
        """Updates a broker."""
        for key, value in data.items():
            setattr(broker, key, value)
        await self.db.commit()
        await self.db.refresh(broker)
        return broker

    async def delete(self, broker: Broker) -> None:
        """Deletes a broker."""
        await self.db.delete(broker)
        await self.db.commit()