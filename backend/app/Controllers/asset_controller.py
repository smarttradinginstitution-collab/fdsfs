from __future__ import annotations
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Repositories.asset_repository import AssetRepository
from app.Repositories.asset_class_repository import AssetClassRepository
from app.Schemas.asset import AssetCreate, AssetRead, AssetUpdate

class AssetController:

    async def get_asset(self, asset_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
        repo = AssetRepository(db)
        asset = await repo.get(asset_id)
        if not asset:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
        return asset

    async def list_assets(self, db: AsyncSession = Depends(get_db)):
        repo = AssetRepository(db)
        return await repo.list()

    async def create_asset(self, asset: AssetCreate, db: AsyncSession = Depends(get_db)):
        asset_repo = AssetRepository(db)

        # Check for symbol uniqueness (case-insensitive)
        if await asset_repo.get_by_symbol(asset.symbol):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An asset with this symbol already exists.",
            )

        # Verify that asset_class_id exists
        asset_class_repo = AssetClassRepository(db)
        if not await asset_class_repo.get(asset.asset_class_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"AssetClass with id '{asset.asset_class_id}' does not exist.",
            )

        return await asset_repo.create(asset)

    async def update_asset(self, asset_id: uuid.UUID, asset: AssetUpdate, db: AsyncSession = Depends(get_db)):
        asset_repo = AssetRepository(db)

        # Verify that the asset exists
        db_asset = await asset_repo.get(asset_id)
        if not db_asset:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

        # If symbol is being updated, check for uniqueness
        if asset.symbol:
            existing_by_symbol = await asset_repo.get_by_symbol(asset.symbol)
            if existing_by_symbol and existing_by_symbol.id != asset_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="An asset with this symbol already exists.",
                )

        # If asset_class_id is being updated, verify it exists
        if asset.asset_class_id:
            asset_class_repo = AssetClassRepository(db)
            if not await asset_class_repo.get(asset.asset_class_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"AssetClass with id '{asset.asset_class_id}' does not exist.",
                )

        updated_asset = await asset_repo.update(asset_id, asset)
        return updated_asset

    async def delete_asset(self, asset_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
        repo = AssetRepository(db)
        success = await repo.delete(asset_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
        return {"ok": True}