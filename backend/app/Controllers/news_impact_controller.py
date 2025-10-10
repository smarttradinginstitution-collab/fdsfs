# app/Controllers/news_impact_controller.py
from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Repositories.news_impact_repository import NewsImpactRepository
from app.Schemas.news_impact import NewsImpactCreate, NewsImpactRead, NewsImpactUpdate
from app.Router.dependencies import get_current_user, get_current_general_account_id, CurrentUser


class NewsImpactController:
    def __init__(self) -> None:
        pass

    async def list_my_news_impacts(
        self,
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> List[NewsImpactRead]:
        """
        Lists all the news impacts of the authenticated user.
        """
        repo = NewsImpactRepository(db)
        news_impacts = await repo.list_news_impacts_by_general_account_id(general_account_id)
        return [NewsImpactRead.from_orm(ni) for ni in news_impacts]

    async def get_news_impact(
        self,
        news_impact_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> NewsImpactRead:
        """
        Retrieves a single news impact by ID, verifying ownership.
        """
        repo = NewsImpactRepository(db)
        news_impact = await repo.get_by_id(news_impact_id)

        if not news_impact:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News Impact not found.")

        if not current_user.is_admin and news_impact.general_account_id != general_account_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access.")

        return NewsImpactRead.from_orm(news_impact)

    async def create_news_impact(
        self,
        news_impact_data: NewsImpactCreate,
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> NewsImpactRead:
        """
        Creates a new news impact for the authenticated user.
        """
        repo = NewsImpactRepository(db)
        new_news_impact = await repo.create(obj_in=news_impact_data, general_account_id=general_account_id)
        return NewsImpactRead.from_orm(new_news_impact)

    async def update_news_impact(
        self,
        news_impact_id: UUID,
        news_impact_data: NewsImpactUpdate,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> NewsImpactRead:
        """
        Updates a news impact, verifying ownership.
        """
        repo = NewsImpactRepository(db)
        news_impact_to_update = await repo.get_by_id(news_impact_id)

        if not news_impact_to_update:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News Impact not found.")

        if not current_user.is_admin and news_impact_to_update.general_account_id != general_account_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access.")

        updated_news_impact = await repo.update(db_obj=news_impact_to_update, obj_in=news_impact_data)
        if not updated_news_impact:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error while updating news impact."
            )

        return NewsImpactRead.from_orm(updated_news_impact)

    async def delete_news_impact(
        self,
        news_impact_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> dict:
        """
        Deletes a news impact, verifying ownership.
        """
        repo = NewsImpactRepository(db)
        news_impact_to_delete = await repo.get_by_id(news_impact_id)

        if not news_impact_to_delete:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News Impact not found.")

        if not current_user.is_admin and news_impact_to_delete.general_account_id != general_account_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access.")

        await repo.delete(db_obj=news_impact_to_delete)

        return {"ok": True, "detail": "News Impact successfully deleted."}