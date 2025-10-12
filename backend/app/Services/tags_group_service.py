# app/Services/tags_group_service.py
from __future__ import annotations
from uuid import UUID
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status

from app.Infrastructure.db import get_db
from app.Repositories.tags_group_repository import TagsGroupRepository
from app.Schemas.tags_group import TagsGroupCreate, TagsGroupUpdate
from app.Models.tags_group import TagsGroup


class TagsGroupService:
    def __init__(
        self,
        db: AsyncSession = Depends(get_db),
    ):
        self.db = db
        self.repo = TagsGroupRepository(db)

    async def create_tags_group(
        self, tags_group_data: TagsGroupCreate, general_account_id: UUID
    ) -> TagsGroup:
        return await self.repo.create_tags_group(
            tags_group_data=tags_group_data, general_account_id=general_account_id
        )

    async def get_tags_group_by_id(
        self, tags_group_id: UUID, general_account_id: UUID
    ) -> TagsGroup:
        db_obj = await self.repo.get_tags_group_by_id(
            tags_group_id=tags_group_id, general_account_id=general_account_id
        )
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tags group not found"
            )
        return db_obj

    async def list_tags_groups_by_general_account_id(
        self, general_account_id: UUID
    ) -> List[TagsGroup]:
        return await self.repo.list_tags_groups_by_general_account_id(
            general_account_id=general_account_id
        )

    async def update_tags_group(
        self, db_obj: TagsGroup, tags_group_data: TagsGroupUpdate
    ) -> TagsGroup:
        return await self.repo.update_tags_group(
            db_obj=db_obj, tags_group_data=tags_group_data
        )

    async def delete_tags_group(self, db_obj: TagsGroup) -> None:
        return await self.repo.delete_tags_group(db_obj=db_obj)
