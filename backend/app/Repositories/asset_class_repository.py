from __future__ import annotations
import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.Models.asset_class import AssetClass
from app.Schemas.asset_class import AssetClassCreate, AssetClassUpdate

class AssetClassRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, asset_class_id: uuid.UUID) -> Optional[AssetClass]:
        result = await self.db.get(AssetClass, asset_class_id)
        return result

    async def get_by_name(self, name: str) -> Optional[AssetClass]:
        stmt = select(AssetClass).where(AssetClass.name == name)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list(self) -> List[AssetClass]:
        stmt = select(AssetClass).order_by(AssetClass.name)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create(self, asset_class: AssetClassCreate) -> AssetClass:
        db_asset_class = AssetClass(**asset_class.model_dump())
        self.db.add(db_asset_class)
        await self.db.commit()
        await self.db.refresh(db_asset_class)
        return db_asset_class

    async def update(self, asset_class_id: uuid.UUID, asset_class_update: AssetClassUpdate) -> Optional[AssetClass]:
        db_asset_class = await self.get(asset_class_id)
        if db_asset_class:
            update_data = asset_class_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_asset_class, key, value)
            await self.db.commit()
            await self.db.refresh(db_asset_class)
        return db_asset_class

    async def delete(self, asset_class_id: uuid.UUID) -> bool:
        db_asset_class = await self.get(asset_class_id)
        if db_asset_class:
            await self.db.delete(db_asset_class)
            await self.db.commit()
            return True
        return False