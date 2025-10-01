from __future__ import annotations
import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.Models.asset_alias import AssetAlias
from app.Schemas.asset_alias import AssetAliasCreate, AssetAliasUpdate

class AssetAliasRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, alias_id: uuid.UUID) -> Optional[AssetAlias]:
        result = await self.db.get(AssetAlias, alias_id)
        return result

    async def list_by_asset(self, asset_id: uuid.UUID) -> List[AssetAlias]:
        stmt = select(AssetAlias).where(AssetAlias.asset_id == asset_id).order_by(AssetAlias.alias)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def list(self) -> List[AssetAlias]:
        stmt = select(AssetAlias).order_by(AssetAlias.alias)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create(self, alias: AssetAliasCreate) -> AssetAlias:
        db_alias = AssetAlias(**alias.model_dump())
        self.db.add(db_alias)
        await self.db.commit()
        await self.db.refresh(db_alias)
        return db_alias

    async def update(self, alias_id: uuid.UUID, alias_update: AssetAliasUpdate) -> Optional[AssetAlias]:
        db_alias = await self.get(alias_id)
        if db_alias:
            update_data = alias_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_alias, key, value)
            await self.db.commit()
            await self.db.refresh(db_alias)
        return db_alias

    async def delete(self, alias_id: uuid.UUID) -> bool:
        db_alias = await self.get(alias_id)
        if db_alias:
            await self.db.delete(db_alias)
            await self.db.commit()
            return True
        return False