from __future__ import annotations
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Repositories.asset_alias_repository import AssetAliasRepository
from app.Repositories.asset_repository import AssetRepository
from app.Repositories.broker_repository import BrokerRepository
from app.Repositories.platform_repository import PlatformRepository
from app.Schemas.asset_alias import AssetAliasCreate, AssetAliasRead, AssetAliasUpdate

class AssetAliasController:

    async def get_alias(self, alias_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
        repo = AssetAliasRepository(db)
        alias = await repo.get(alias_id)
        if not alias:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset alias not found")
        return alias

    async def list_aliases(self, db: AsyncSession = Depends(get_db)):
        repo = AssetAliasRepository(db)
        return await repo.list()

    async def list_aliases_for_asset(self, asset_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
        repo = AssetAliasRepository(db)
        return await repo.list_by_asset(asset_id)

    async def create_alias(self, alias: AssetAliasCreate, db: AsyncSession = Depends(get_db)):
        # Validate foreign keys
        await self._validate_fks(db, asset_id=alias.asset_id, broker_id=alias.broker_id, platform_id=alias.platform_id)

        repo = AssetAliasRepository(db)
        return await repo.create(alias)

    async def update_alias(self, alias_id: uuid.UUID, alias: AssetAliasUpdate, db: AsyncSession = Depends(get_db)):
        repo = AssetAliasRepository(db)

        db_alias = await repo.get(alias_id)
        if not db_alias:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset alias not found")

        # Validate foreign keys if they are being updated
        await self._validate_fks(db, broker_id=alias.broker_id, platform_id=alias.platform_id)

        updated_alias = await repo.update(alias_id, alias)
        return updated_alias

    async def delete_alias(self, alias_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
        repo = AssetAliasRepository(db)
        success = await repo.delete(alias_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset alias not found")
        return {"ok": True}

    async def _validate_fks(self, db: AsyncSession, asset_id: uuid.UUID = None, broker_id: uuid.UUID = None, platform_id: uuid.UUID = None):
        if asset_id:
            asset_repo = AssetRepository(db)
            if not await asset_repo.get(asset_id):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Asset with id '{asset_id}' does not exist.")

        if broker_id:
            broker_repo = BrokerRepository(db)
            if not await broker_repo.get_by_id(broker_id):
                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Broker with id '{broker_id}' does not exist.")

        if platform_id:
            platform_repo = PlatformRepository(db)
            if not await platform_repo.get(platform_id):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Platform with id '{platform_id}' does not exist.")