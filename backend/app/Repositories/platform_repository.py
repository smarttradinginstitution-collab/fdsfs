# app/Repositories/platform_repository.py
from __future__ import annotations

import uuid
from typing import List

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.Models.broker import Broker
from app.Models.platform import Platform
from app.Schemas.platform import PlatformCreate, PlatformUpdate


class PlatformRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, platform_id: uuid.UUID) -> Platform | None:
        return await self.db.get(Platform, platform_id)

    async def get_by_name(self, name: str) -> Platform | None:
        result = await self.db.execute(
            select(Platform).where(Platform.name == name)
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self, skip: int = 0, limit: int = 100
    ) -> list[Platform]:
        result = await self.db.execute(select(Platform).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_multi_with_brokers(
        self, skip: int = 0, limit: int = 100
    ) -> list[Platform]:
        result = await self.db.execute(
            select(Platform)
            .options(joinedload(Platform.brokers))
            .offset(skip)
            .limit(limit)
        )
        return result.unique().scalars().all()

    async def create(self, platform_in: PlatformCreate) -> Platform:
        stmt = select(Platform).where(Platform.name == platform_in.name)
        existing_platform = await self.db.execute(stmt)
        if existing_platform.scalars().first():
            raise HTTPException(
                status_code=409,
                detail="A platform with this name already exists.",
            )

        brokers = []
        if platform_in.brokers:
            result = await self.db.execute(
                select(Broker).where(Broker.id.in_(platform_in.brokers))
            )
            brokers = result.scalars().all()

        db_platform = Platform(name=platform_in.name, brokers=brokers)
        self.db.add(db_platform)
        await self.db.commit()
        await self.db.refresh(db_platform)
        return db_platform

    async def update(
        self, platform: Platform, platform_in: PlatformUpdate
    ) -> Platform:
        platform_data = platform_in.model_dump(exclude_unset=True)

        if "name" in platform_data and platform_data["name"] != platform.name:
            stmt = select(Platform).where(
                Platform.name == platform_data["name"],
                Platform.id != platform.id
            )
            existing_platform = await self.db.execute(stmt)
            if existing_platform.scalars().first():
                raise HTTPException(
                    status_code=409,
                    detail="A platform with this name already exists.",
                )

        for field, value in platform_data.items():
            if field != "brokers":
                setattr(platform, field, value)

        if platform_in.brokers is not None:
            if platform_in.brokers:
                result = await self.db.execute(
                    select(Broker).where(Broker.id.in_(platform_in.brokers))
                )
                brokers = result.scalars().all()
                platform.brokers = brokers
            else:
                platform.brokers = []

        self.db.add(platform)
        await self.db.commit()
        await self.db.refresh(platform)
        return platform

    async def delete(self, platform: Platform) -> Platform:
        await self.db.delete(platform)
        await self.db.commit()
        return platform