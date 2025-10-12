# app/Services/tags_group_service.py
from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Repositories.tags_group_repository import TagsGroupRepository
from app.Schemas.tags_group import (
    TagsGroupCreate,
    TagsGroupRead,
    TagsGroupUpdate,
    TagsGroupReorder,
)


class TagsGroupService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
        self.repo = TagsGroupRepository(db)

    async def create_tags_group(
        self, tags_group_data: TagsGroupCreate, general_account_id: UUID
    ) -> TagsGroupRead:
        """
        Creates a new tags group for the authenticated user.
        """
        # Check for duplicates
        existing_group = await self.repo.get_by_name(
            name=tags_group_data.name, general_account_id=general_account_id
        )
        if existing_group:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A tags group with this name already exists.",
            )

        new_tags_group = await self.repo.create_tags_group(
            tags_group_data=tags_group_data, general_account_id=general_account_id
        )
        await self.db.commit()
        await self.db.refresh(new_tags_group)
        return TagsGroupRead.model_validate(new_tags_group)

    async def list_tags_groups(
        self, general_account_id: UUID
    ) -> List[TagsGroupRead]:
        """
        Lists all tags groups for the authenticated user's general account.
        """
        tags_groups = await self.repo.list_tags_groups_by_general_account_id(
            general_account_id
        )
        return [TagsGroupRead.model_validate(tg) for tg in tags_groups]

    async def get_tags_group(
        self, tags_group_id: UUID, general_account_id: UUID
    ) -> TagsGroupRead:
        """
        Retrieves a single tags group by its ID, verifying ownership.
        """
        tags_group = await self.repo.get_tags_group_by_id(
            tags_group_id, general_account_id
        )

        if not tags_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tags Group not found or access denied.",
            )
        return TagsGroupRead.model_validate(tags_group)

    async def update_tags_group(
        self,
        tags_group_id: UUID,
        tags_group_data: TagsGroupUpdate,
        general_account_id: UUID,
    ) -> TagsGroupRead:
        """
        Updates a tags group, verifying ownership.
        """
        tags_group_to_update = await self.repo.get_tags_group_by_id(
            tags_group_id, general_account_id
        )

        if not tags_group_to_update:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tags Group not found or access denied.",
            )

        updated_tags_group = await self.repo.update_tags_group(
            db_obj=tags_group_to_update, tags_group_data=tags_group_data
        )
        await self.db.commit()
        await self.db.refresh(updated_tags_group)
        return TagsGroupRead.model_validate(updated_tags_group)

    async def delete_tags_group(
        self, tags_group_id: UUID, general_account_id: UUID
    ) -> None:
        """
        Deletes a tags group and all its associated tags, verifying ownership.
        """
        tags_group_to_delete = await self.repo.get_tags_group_by_id(
            tags_group_id, general_account_id
        )

        if not tags_group_to_delete:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tags Group not found or access denied.",
            )

        await self.repo.delete_tags_group(db_obj=tags_group_to_delete)
        await self.db.commit()

    async def reorder_tags_groups(
        self, reorder_data: TagsGroupReorder, general_account_id: UUID
    ) -> None:
        """
        Reorders the tags groups for the user.
        """
        await self.repo.reorder_groups(
            general_account_id=general_account_id, group_ids=reorder_data.group_ids
        )
        await self.db.commit()