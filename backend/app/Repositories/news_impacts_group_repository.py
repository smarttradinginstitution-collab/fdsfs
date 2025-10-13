# app/Repositories/news_impacts_group_repository.py
from __future__ import annotations

from typing import Optional, Sequence, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.Models.news_impacts_group import NewsImpactsGroup
from app.Schemas.news_impacts_group import NewsImpactsGroupCreate, NewsImpactsGroupUpdate


class NewsImpactsGroupRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_news_impacts_group(
        self, news_impacts_group_data: NewsImpactsGroupCreate, general_account_id: UUID
    ) -> NewsImpactsGroup:
        """Creates a new news impacts group."""
        db_news_impacts_group = NewsImpactsGroup(
            **news_impacts_group_data.model_dump(), general_account_id=general_account_id
        )
        self.db.add(db_news_impacts_group)
        await self.db.flush()
        group_id = db_news_impacts_group.id
        await self.db.commit()

        created_group = await self.get_news_impacts_group_by_id(group_id, general_account_id)
        if not created_group:
            raise Exception("Failed to re-fetch created news impacts group")
        return created_group

    async def get_news_impacts_group_by_id(
        self, news_impacts_group_id: UUID, general_account_id: UUID
    ) -> Optional[NewsImpactsGroup]:
        """Retrieves a specific news impacts group by ID for a given general account."""
        stmt = (
            select(NewsImpactsGroup)
            .options(selectinload(NewsImpactsGroup.news_impacts))
            .where(
                NewsImpactsGroup.id == news_impacts_group_id,
                NewsImpactsGroup.general_account_id == general_account_id,
            )
            .limit(1)
        )
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def list_news_impacts_groups_by_general_account_id(
        self, general_account_id: UUID
    ) -> Sequence[NewsImpactsGroup]:
        """Lists all news impacts groups for a given general_account_id."""
        stmt = (
            select(NewsImpactsGroup)
            .options(selectinload(NewsImpactsGroup.news_impacts))
            .where(NewsImpactsGroup.general_account_id == general_account_id)
            .order_by(NewsImpactsGroup.position.asc(), NewsImpactsGroup.name.asc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def update_news_impacts_group(
        self, db_obj: NewsImpactsGroup, news_impacts_group_data: NewsImpactsGroupUpdate
    ) -> NewsImpactsGroup:
        """Updates an existing news impacts group."""
        update_data = news_impacts_group_data.model_dump(exclude_unset=True)

        if update_data:
            for field, value in update_data.items():
                setattr(db_obj, field, value)

            self.db.add(db_obj)
            await self.db.commit()

        updated_group = await self.get_news_impacts_group_by_id(
            db_obj.id, db_obj.general_account_id
        )
        if not updated_group:
            raise Exception("Failed to re-fetch updated news impacts group")
        return updated_group

    async def delete_news_impacts_group(self, db_obj: NewsImpactsGroup) -> None:
        """Deletes a news impacts group."""
        await self.db.delete(db_obj)
        await self.db.commit()

    async def reorder_groups(
        self, general_account_id: UUID, group_ids: List[UUID]
    ) -> None:
        """
        Updates the position of multiple news impacts groups in a single transaction.
        """
        for index, group_id in enumerate(group_ids):
            stmt = (
                select(NewsImpactsGroup)
                .where(
                    NewsImpactsGroup.id == group_id,
                    NewsImpactsGroup.general_account_id == general_account_id,
                )
            )
            result = await self.db.execute(stmt)
            group = result.scalars().first()
            if group:
                group.position = index

        await self.db.commit()
