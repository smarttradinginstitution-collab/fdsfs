from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from fastapi import HTTPException
from app.Models.asset_market import AssetMarket
from app.Schemas.asset_market import AssetMarketCreate, AssetMarketUpdate

class AssetMarketRepository:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create(self, market: AssetMarketCreate) -> AssetMarket:
        existing = await self.get_by_name(market.name)
        if existing:
            raise HTTPException(
                status_code=409,
                detail="An asset market with this name already exists.",
            )
        new_market = AssetMarket(name=market.name)
        self.db.add(new_market)
        await self.db.commit()
        await self.db.refresh(new_market)
        return new_market

    async def get(self, market_id: UUID) -> AssetMarket | None:
        result = await self.db.execute(select(AssetMarket).where(AssetMarket.id == market_id))
        return result.scalars().first()

    async def get_by_name(self, name: str) -> AssetMarket | None:
        result = await self.db.execute(select(AssetMarket).where(AssetMarket.name == name))
        return result.scalars().first()

    async def list(self) -> list[AssetMarket]:
        result = await self.db.execute(select(AssetMarket).order_by(AssetMarket.name))
        return result.scalars().all()

    async def update(self, market_id: UUID, market_data: AssetMarketUpdate) -> AssetMarket | None:
        market = await self.get(market_id)
        if market:
            update_data = market_data.model_dump(exclude_unset=True)
            if "name" in update_data and update_data["name"] != market.name:
                existing = await self.get_by_name(update_data["name"])
                if existing:
                    raise HTTPException(
                        status_code=409,
                        detail="An asset market with this name already exists.",
                    )
            for key, value in update_data.items():
                setattr(market, key, value)
            await self.db.commit()
            await self.db.refresh(market)
        return market

    async def delete(self, market_id: UUID) -> bool:
        market = await self.get(market_id)
        if market:
            await self.db.delete(market)
            await self.db.commit()
            return True
        return False