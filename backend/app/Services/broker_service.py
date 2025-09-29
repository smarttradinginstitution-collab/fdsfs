# app/Services/broker_service.py
from __future__ import annotations

import uuid
from typing import List
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Repositories.broker_repository import BrokerRepository
from app.Models.broker import Broker
from app.Schemas.broker import BrokerCreate, BrokerUpdate


class BrokerService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.repo = BrokerRepository(db)

    async def create_broker(self, data: BrokerCreate) -> Broker:
        """Creates a new broker."""
        # Check if a broker with the same name already exists
        existing_broker = await self.repo.get_by_name(data.name)
        if existing_broker:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A broker with this name already exists.",
            )

        return await self.repo.create(data.dict())

    async def get_all_brokers(self) -> List[Broker]:
        """Returns a list of all brokers."""
        return await self.repo.list_all()

    async def get_broker_by_id(self, broker_id: uuid.UUID) -> Broker:
        """Returns a broker by its ID."""
        broker = await self.repo.get_by_id(broker_id)
        if not broker:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Broker not found.",
            )
        return broker

    async def update_broker(
        self, broker_id: uuid.UUID, data: BrokerUpdate
    ) -> Broker:
        """Updates a broker's name."""
        broker = await self.get_broker_by_id(broker_id)

        # Check if another broker with the new name already exists
        if data.name != broker.name:
            existing_broker = await self.repo.get_by_name(data.name)
            if existing_broker:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A broker with this name already exists.",
                )

        return await self.repo.update(broker, data.dict(exclude_unset=True))

    async def delete_broker(self, broker_id: uuid.UUID) -> None:
        """Deletes a broker."""
        broker = await self.repo.get_by_id_with_relationships(broker_id)

        if not broker:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Broker not found.",
            )

        # Check for active relationships
        if (
            broker.trading_accounts
            or broker.platforms
            or broker.asset_aliases
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete broker because it is associated with other resources.",
            )

        await self.repo.delete(broker)