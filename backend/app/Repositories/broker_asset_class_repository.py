from __future__ import annotations

import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.Models.broker_asset_class import BrokerAssetClass
from app.Schemas.broker_asset_class import BrokerAssetClassCreate


class BrokerAssetClassRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, broker_id: uuid.UUID, data: BrokerAssetClassCreate
    ) -> BrokerAssetClass:
        """Creates a new association between a broker and an asset class."""
        association = BrokerAssetClass(
            broker_id=broker_id, asset_class_id=data.asset_class_id
        )
        self.db.add(association)
        await self.db.commit()
        await self.db.refresh(association)
        return association

    async def delete(self, association: BrokerAssetClass) -> None:
        """Deletes an association."""
        await self.db.delete(association)
        await self.db.commit()

    async def get_by_broker_and_asset_class(
        self, broker_id: uuid.UUID, asset_class_id: uuid.UUID
    ) -> BrokerAssetClass | None:
        """Finds an association by broker and asset class."""
        stmt = select(BrokerAssetClass).where(
            BrokerAssetClass.broker_id == broker_id,
            BrokerAssetClass.asset_class_id == asset_class_id,
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_by_broker_id(self, broker_id: uuid.UUID) -> List[BrokerAssetClass]:
        """Lists all associations for a given broker, with asset classes eagerly loaded."""
        stmt = (
            select(BrokerAssetClass)
            .where(BrokerAssetClass.broker_id == broker_id)
            .options(selectinload(BrokerAssetClass.asset_class))
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
