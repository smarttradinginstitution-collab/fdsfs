from __future__ import annotations

from typing import Optional, Sequence
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.Models.news_impact import NewsImpact
from app.Models.news_impacts_group import NewsImpactsGroup
from app.Schemas.news_impact import NewsImpactCreate, NewsImpactUpdate


class NewsImpactRepository:
    """Repository for NewsImpact CRUD operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, news_impact_id: UUID) -> Optional[NewsImpact]:
        """Get a specific news impact by ID."""
        stmt = select(NewsImpact).where(NewsImpact.id == news_impact_id).options(selectinload(NewsImpact.group)).limit(1)
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def create(self, obj_in: NewsImpactCreate, group_id: UUID) -> NewsImpact:
        """Create a new news impact."""
        data = obj_in.model_dump()
        data.pop("group_id", None)
        db_obj = NewsImpact(
            **data,
            group_id=group_id
        )
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: NewsImpact, obj_in: NewsImpactUpdate) -> NewsImpact:
        """Update an existing news impact."""
        update_data = obj_in.model_dump(exclude_unset=True)
        if not update_data:
            return db_obj

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: NewsImpact) -> None:
        """Delete a news impact."""
        await self.db.delete(db_obj)
        await self.db.commit()

    async def list_news_impacts_by_general_account_id(
        self, general_account_id: UUID
    ) -> Sequence[NewsImpact]:
        """List all news impacts for a given general_account_id."""
        stmt = (
            select(NewsImpact)
            .join(NewsImpact.group)
            .where(NewsImpactsGroup.general_account_id == general_account_id)
            .order_by(NewsImpact.name.asc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()