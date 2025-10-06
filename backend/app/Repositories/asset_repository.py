from __future__ import annotations
import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.Models.asset import Asset
from app.Schemas.asset import AssetCreate, AssetUpdate

class AssetRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, asset_id: uuid.UUID) -> Optional[Asset]:
        stmt = (
            select(Asset)
            .where(Asset.id == asset_id)
            .options(
                joinedload(Asset.asset_class),
                joinedload(Asset.asset_market)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_by_symbol(self, symbol: str) -> Optional[Asset]:
        stmt = (
            select(Asset)
            .where(Asset.symbol_norm == symbol.upper().strip())
            .options(
                joinedload(Asset.asset_class),
                joinedload(Asset.asset_market)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list(self) -> List[Asset]:
        stmt = (
            select(Asset)
            .order_by(Asset.symbol)
            .options(
                joinedload(Asset.asset_class),
                joinedload(Asset.asset_market)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create(self, asset: AssetCreate) -> Asset:
        db_asset = Asset(**asset.model_dump())
        self.db.add(db_asset)
        await self.db.commit()
        # Re-fetch to load relationships
        return await self.get(db_asset.id)

    async def update(self, asset_id: uuid.UUID, asset_update: AssetUpdate) -> Optional[Asset]:
        db_asset = await self.get(asset_id)
        if db_asset:
            update_data = asset_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_asset, key, value)
            await self.db.commit()
            # Re-fetch to load relationships
            return await self.get(asset_id)
        return None

    async def delete(self, asset_id: uuid.UUID) -> bool:
        db_asset = await self.get(asset_id)
        if db_asset:
            await self.db.delete(db_asset)
            await self.db.commit()
            return True
        return False