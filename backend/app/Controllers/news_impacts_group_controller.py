# app/Controllers/news_impacts_group_controller.py
from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Repositories.news_impacts_group_repository import NewsImpactsGroupRepository
from app.Schemas.news_impacts_group import (
    NewsImpactsGroupCreate,
    NewsImpactsGroupRead,
    NewsImpactsGroupUpdate,
    NewsImpactsGroupReorder,
)
from app.Router.dependencies import get_current_general_account_id

router = APIRouter(
    prefix="/me/news-impacts-groups",
    tags=["News Impacts Groups"],
)


@router.post(
    "",
    response_model=NewsImpactsGroupRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new news impacts group",
)
async def create_news_impacts_group(
    news_impacts_group_data: NewsImpactsGroupCreate,
    general_account_id: UUID = Depends(get_current_general_account_id),
    db: AsyncSession = Depends(get_db),
) -> NewsImpactsGroupRead:
    repo = NewsImpactsGroupRepository(db)
    new_group = await repo.create_news_impacts_group(
        news_impacts_group_data=news_impacts_group_data, general_account_id=general_account_id
    )
    return new_group


@router.get(
    "",
    response_model=List[NewsImpactsGroupRead],
    summary="List all news impacts groups",
)
async def list_news_impacts_groups(
    general_account_id: UUID = Depends(get_current_general_account_id),
    db: AsyncSession = Depends(get_db),
) -> List[NewsImpactsGroupRead]:
    repo = NewsImpactsGroupRepository(db)
    groups = await repo.list_news_impacts_groups_by_general_account_id(general_account_id)
    return groups


@router.get(
    "/{group_id}",
    response_model=NewsImpactsGroupRead,
    summary="Get a specific news impacts group",
)
async def get_news_impacts_group(
    group_id: UUID,
    general_account_id: UUID = Depends(get_current_general_account_id),
    db: AsyncSession = Depends(get_db),
) -> NewsImpactsGroupRead:
    repo = NewsImpactsGroupRepository(db)
    group = await repo.get_news_impacts_group_by_id(group_id, general_account_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News Impacts Group not found.",
        )
    return group


@router.put(
    "/{group_id}",
    response_model=NewsImpactsGroupRead,
    summary="Update a news impacts group",
)
async def update_news_impacts_group(
    group_id: UUID,
    news_impacts_group_data: NewsImpactsGroupUpdate,
    general_account_id: UUID = Depends(get_current_general_account_id),
    db: AsyncSession = Depends(get_db),
) -> NewsImpactsGroupRead:
    repo = NewsImpactsGroupRepository(db)
    group_to_update = await repo.get_news_impacts_group_by_id(
        group_id, general_account_id
    )
    if not group_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News Impacts Group not found.",
        )
    updated_group = await repo.update_news_impacts_group(
        db_obj=group_to_update, news_impacts_group_data=news_impacts_group_data
    )
    return updated_group


@router.delete(
    "/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a news impacts group",
)
async def delete_news_impacts_group(
    group_id: UUID,
    general_account_id: UUID = Depends(get_current_general_account_id),
    db: AsyncSession = Depends(get_db),
):
    repo = NewsImpactsGroupRepository(db)
    group_to_delete = await repo.get_news_impacts_group_by_id(
        group_id, general_account_id
    )
    if not group_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News Impacts Group not found.",
        )
    await repo.delete_news_impacts_group(db_obj=group_to_delete)
    return None


@router.post(
    "/reorder",
    status_code=status.HTTP_200_OK,
    summary="Reorder news impacts groups",
)
async def reorder_news_impacts_groups(
    reorder_data: NewsImpactsGroupReorder,
    general_account_id: UUID = Depends(get_current_general_account_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    repo = NewsImpactsGroupRepository(db)
    await repo.reorder_groups(
        general_account_id=general_account_id, group_ids=reorder_data.group_ids
    )
    return {"message": "Groups reordered successfully."}
