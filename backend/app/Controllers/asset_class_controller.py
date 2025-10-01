from __future__ import annotations
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Repositories.asset_class_repository import AssetClassRepository
from app.Schemas.asset_class import AssetClassCreate, AssetClassRead, AssetClassUpdate

class AssetClassController:

    async def get_asset_class(self, asset_class_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
        repo = AssetClassRepository(db)
        asset_class = await repo.get(asset_class_id)
        if not asset_class:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset class not found")
        return asset_class

    async def list_asset_classes(self, db: AsyncSession = Depends(get_db)):
        repo = AssetClassRepository(db)
        return await repo.list()

    async def create_asset_class(self, asset_class: AssetClassCreate, db: AsyncSession = Depends(get_db)):
        repo = AssetClassRepository(db)
        # Check if name is unique
        if await repo.get_by_name(asset_class.name):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An asset class with this name already exists.",
            )
        return await repo.create(asset_class)

    async def update_asset_class(self, asset_class_id: uuid.UUID, asset_class: AssetClassUpdate, db: AsyncSession = Depends(get_db)):
        repo = AssetClassRepository(db)
        # Check if the new name is already taken by another asset class
        existing_by_name = await repo.get_by_name(asset_class.name)
        if existing_by_name and existing_by_name.id != asset_class_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An asset class with this name already exists.",
            )

        updated_asset_class = await repo.update(asset_class_id, asset_class)

        if not updated_asset_class:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset class not found")
        return updated_asset_class

    async def delete_asset_class(self, asset_class_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
        repo = AssetClassRepository(db)
        success = await repo.delete(asset_class_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset class not found")
        return {"ok": True}