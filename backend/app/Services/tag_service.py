# app/Services/tag_service.py
from __future__ import annotations

from uuid import UUID
from typing import List, Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Repositories.tag_repository import TagRepository
from app.Repositories.tags_group_repository import TagsGroupRepository
from app.Schemas.tag import TagCreate, TagRead, TagUpdate
from app.Router.dependencies import CurrentUser


class TagService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
        self.tag_repo = TagRepository(db)
        self.tags_group_repo = TagsGroupRepository(db)

    async def create_tag(
        self, tag_data: TagCreate, general_account_id: UUID
    ) -> TagRead:
        """
        Creates a new tag for the authenticated user.
        Verifies that the group exists and belongs to the user.
        """
        group = await self.tags_group_repo.get_tags_group_by_id(
            tag_data.group_id, general_account_id
        )
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tags Group not found or access denied.",
            )

        new_tag = await self.tag_repo.create_tag(tag_data)
        await self.db.commit()
        await self.db.refresh(new_tag)
        return TagRead.model_validate(new_tag)

    async def get_tag(
        self, tag_id: UUID, current_user: CurrentUser, general_account_id: UUID
    ) -> TagRead:
        """
        Retrieves a single tag by its ID, verifying ownership.
        """
        tag = await self.tag_repo.get_tag_by_id(tag_id)

        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found."
            )

        # Ownership check (or if the user is an admin)
        if not tag.group or (
            not current_user.is_admin
            and tag.group.general_account_id != general_account_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied."
            )

        return TagRead.model_validate(tag)

    async def list_my_tags(self, general_account_id: UUID) -> List[TagRead]:
        """
        Lists all tags for the authenticated user.
        """
        tags = await self.tag_repo.list_tags_by_general_account_id(general_account_id)
        return [TagRead.model_validate(t) for t in tags]

    async def update_tag(
        self,
        tag_id: UUID,
        tag_data: TagUpdate,
        current_user: CurrentUser,
        general_account_id: UUID,
    ) -> TagRead:
        """
        Updates a tag, verifying ownership.
        """
        tag_to_update = await self.tag_repo.get_tag_by_id(tag_id)

        if not tag_to_update:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found."
            )

        # Ownership check
        if not tag_to_update.group or (
            not current_user.is_admin
            and tag_to_update.group.general_account_id != general_account_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied."
            )

        updated_tag = await self.tag_repo.update_tag(
            db_obj=tag_to_update, tag_data=tag_data
        )
        await self.db.commit()
        await self.db.refresh(updated_tag)
        return TagRead.model_validate(updated_tag)

    async def delete_tag(
        self, tag_id: UUID, current_user: CurrentUser, general_account_id: UUID
    ) -> None:
        """
        Deletes a tag, verifying ownership.
        """
        tag_to_delete = await self.tag_repo.get_tag_by_id(tag_id)

        if not tag_to_delete:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found."
            )

        # Ownership check
        if not tag_to_delete.group or (
            not current_user.is_admin
            and tag_to_delete.group.general_account_id != general_account_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied."
            )

        await self.tag_repo.delete_tag(db_obj=tag_to_delete)
        await self.db.commit()