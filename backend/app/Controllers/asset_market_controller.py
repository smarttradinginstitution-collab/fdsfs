from __future__ import annotations
import uuid
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Repositories.asset_market_repository import AssetMarketRepository
from app.Schemas.asset_market import AssetMarketCreate, AssetMarketRead, AssetMarketUpdate

class AssetMarketController:

    async def get_asset_market(self, asset_market_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> AssetMarketRead:
        repo = AssetMarketRepository(db)
        asset_market = await repo.get(asset_market_id)
        if not asset_market:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset market not found")
        return asset_market

    async def list_asset_markets(self, db: AsyncSession = Depends(get_db)) -> list[AssetMarketRead]:
        repo = AssetMarketRepository(db)
        return await repo.list()

    async def create_asset_market(self, asset_market: AssetMarketCreate, db: AsyncSession = Depends(get_db)) -> AssetMarketRead:
        repo = AssetMarketRepository(db)

        if await repo.get_by_name(asset_market.name):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An asset market with this name already exists.",
            )
        if asset_market.code and await repo.get_by_code(asset_market.code):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An asset market with this code already exists.",
            )

        return await repo.create(asset_market)

    async def update_asset_market(self, asset_market_id: uuid.UUID, asset_market: AssetMarketUpdate, db: AsyncSession = Depends(get_db)) -> AssetMarketRead:
        repo = AssetMarketRepository(db)

        if asset_market.name:
            existing_by_name = await repo.get_by_name(asset_market.name)
            if existing_by_name and existing_by_name.id != asset_market_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="An asset market with this name already exists.",
                )

        if asset_market.code:
            existing_by_code = await repo.get_by_code(asset_market.code)
            if existing_by_code and existing_by_code.id != asset_market_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="An asset market with this code already exists.",
                )

        updated_asset_market = await repo.update(asset_market_id, asset_market)

        if not updated_asset_market:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset market not found")
        return updated_asset_market

    async def delete_asset_market(self, asset_market_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
        repo = AssetMarketRepository(db)
        success = await repo.delete(asset_market_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset market not found")
        return {"ok": True}