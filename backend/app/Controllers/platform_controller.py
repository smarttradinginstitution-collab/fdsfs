# app/Controllers/platform_controller.py
from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.broker import Broker
from app.Models.platform import Platform
from app.Repositories.platform_repository import PlatformRepository
from app.Schemas.platform import PlatformCreate, PlatformUpdate


class PlatformController:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.platform_repo = PlatformRepository(db)

    async def get_platform_by_id(self, platform_id: uuid.UUID) -> Platform:
        platform = await self.platform_repo.get(platform_id)
        if not platform:
            raise HTTPException(status_code=404, detail="Platform not found")
        return platform

    async def get_all_platforms(self, skip: int, limit: int) -> list[Platform]:
        return await self.platform_repo.get_multi(skip=skip, limit=limit)

    async def get_platform_summary(self, platform_id: uuid.UUID) -> Platform:
        platform = await self.platform_repo.get_summary(platform_id)
        if not platform:
            raise HTTPException(status_code=404, detail="Platform not found")
        return platform

    async def create_platform(self, platform_in: PlatformCreate) -> Platform:
        existing_platform = await self.platform_repo.get_by_name(platform_in.name)
        if existing_platform:
            raise HTTPException(
                status_code=409,
                detail="A platform with this name already exists.",
            )

        if platform_in.brokers:
            for broker_id in platform_in.brokers:
                broker = await self.db.get(Broker, broker_id)
                if not broker:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Broker with id {broker_id} not found",
                    )

        return await self.platform_repo.create(platform_in)

    async def update_platform(
        self, platform_id: uuid.UUID, platform_in: PlatformUpdate
    ) -> Platform:
        # Eagerly load the platform with its brokers to prevent lazy loading issues
        platform = await self.platform_repo.get_summary(platform_id)
        if not platform:
            raise HTTPException(status_code=404, detail="Platform not found")

        if platform_in.name and platform_in.name != platform.name:
            existing_platform = await self.platform_repo.get_by_name(platform_in.name)
            if existing_platform:
                raise HTTPException(
                    status_code=409,
                    detail="A platform with this name already exists.",
                )

        if platform_in.brokers is not None:
            for broker_id in platform_in.brokers:
                broker = await self.db.get(Broker, broker_id)
                if not broker:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Broker with id {broker_id} not found",
                    )

        return await self.platform_repo.update(platform, platform_in)

    async def delete_platform(self, platform_id: uuid.UUID) -> Platform:
        platform = await self.get_platform_by_id(platform_id)
        return await self.platform_repo.delete(platform)