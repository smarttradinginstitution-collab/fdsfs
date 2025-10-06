from __future__ import annotations
import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.Models.asset_market import AssetMarket
from app.Schemas.asset_market import AssetMarketCreate, AssetMarketUpdate

class AssetMarketRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, asset_market_id: uuid.UUID) -> Optional[AssetMarket]:
        """Fetches an asset market by its ID."""
        result = await self.db.get(AssetMarket, asset_market_id)
        return result

    async def get_by_name(self, name: str) -> Optional[AssetMarket]:
        """Fetches an asset market by its name."""
        stmt = select(AssetMarket).where(AssetMarket.name == name)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_by_code(self, code: str) -> Optional[AssetMarket]:
        """Fetches an asset market by its code."""
        stmt = select(AssetMarket).where(AssetMarket.code == code)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list(self) -> List[AssetMarket]:
        """Fetches all asset markets."""
        stmt = select(AssetMarket).order_by(AssetMarket.name)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create(self, asset_market: AssetMarketCreate) -> AssetMarket:
        """Creates a new asset market."""
        db_asset_market = AssetMarket(**asset_market.model_dump())
        self.db.add(db_asset_market)
        await self.db.commit()
        await self.db.refresh(db_asset_market)
        return db_asset_market

    async def update(self, asset_market_id: uuid.UUID, asset_market_update: AssetMarketUpdate) -> Optional[AssetMarket]:
        """Updates an existing asset market."""
        db_asset_market = await self.get(asset_market_id)
        if db_asset_market:
            update_data = asset_market_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_asset_market, key, value)
            await self.db.commit()
            await self.db.refresh(db_asset_market)
        return db_asset_market

    async def delete(self, asset_market_id: uuid.UUID) -> bool:
        """Deletes an asset market."""
        db_asset_market = await self.get(asset_market_id)
        if db_asset_market:
            await self.db.delete(db_asset_market)
            await self.db.commit()
            return True
        return False