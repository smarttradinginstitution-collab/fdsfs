# app/Controllers/news_impact_controller.py
from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Repositories.news_impact_repository import NewsImpactRepository
from app.Repositories.news_impacts_group_repository import NewsImpactsGroupRepository
from app.Schemas.news_impact import NewsImpactCreate, NewsImpactRead, NewsImpactUpdate
from app.Router.dependencies import get_current_user, get_current_general_account_id, CurrentUser

router = APIRouter(
    prefix="/me/news-impacts",
    tags=["News Impacts"],
)


@router.get("/", response_model=List[NewsImpactRead])
async def list_my_news_impacts(
    general_account_id: UUID = Depends(get_current_general_account_id),
    db: AsyncSession = Depends(get_db),
) -> List[NewsImpactRead]:
    """
    Lists all the news impacts of the authenticated user.
    """
    repo = NewsImpactRepository(db)
    news_impacts = await repo.list_news_impacts_by_general_account_id(general_account_id)
    return news_impacts


@router.get("/{news_impact_id}", response_model=NewsImpactRead)
async def get_news_impact(
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

    if not news_impact or not news_impact.group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News Impact not found.")

    if not current_user.is_admin and news_impact.group.general_account_id != general_account_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access.")

    return news_impact


@router.post("", response_model=NewsImpactRead, status_code=status.HTTP_201_CREATED)
async def create_news_impact(
    news_impact_data: NewsImpactCreate,
    general_account_id: UUID = Depends(get_current_general_account_id),
    db: AsyncSession = Depends(get_db),
) -> NewsImpactRead:
    """
    Creates a new news impact for the authenticated user.
    """
    group_repo = NewsImpactsGroupRepository(db)
    group = await group_repo.get_news_impacts_group_by_id(
        news_impact_data.group_id, general_account_id
    )
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News Impacts Group not found or access denied.",
        )

    repo = NewsImpactRepository(db)
    new_news_impact = await repo.create(
        obj_in=news_impact_data, group_id=news_impact_data.group_id
    )
    return new_news_impact


@router.put("/{news_impact_id}", response_model=NewsImpactRead)
async def update_news_impact(
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

    if not news_impact_to_update or not news_impact_to_update.group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News Impact not found.")

    if not current_user.is_admin and news_impact_to_update.group.general_account_id != general_account_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access.")

    updated_news_impact = await repo.update(db_obj=news_impact_to_update, obj_in=news_impact_data)
    return updated_news_impact


@router.delete("/{news_impact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_news_impact(
    news_impact_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    general_account_id: UUID = Depends(get_current_general_account_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Deletes a news impact, verifying ownership.
    """
    repo = NewsImpactRepository(db)
    news_impact_to_delete = await repo.get_by_id(news_impact_id)

    if not news_impact_to_delete or not news_impact_to_delete.group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News Impact not found.")

    if not current_user.is_admin and news_impact_to_delete.group.general_account_id != general_account_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access.")

    await repo.delete(db_obj=news_impact_to_delete)
    return None
