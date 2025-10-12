# app/Controllers/tags_group_controller.py
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
from app.Router.dependencies import get_current_general_account_id


async def create_tags_group(
    tags_group_data: TagsGroupCreate,
    general_account_id: UUID = Depends(get_current_general_account_id),
    db: AsyncSession = Depends(get_db),
) -> TagsGroupRead:
    """
    Creates a new tags group for the authenticated user.
    """
    repo = TagsGroupRepository(db)
    # Create the object in the session
    db_tags_group = await repo.create_tags_group(
        tags_group_data=tags_group_data, general_account_id=general_account_id
    )
    # Commit to get the ID
    await db.commit()
    # Re-fetch with relationships loaded
    new_tags_group = await repo.get_tags_group_by_id(
        tags_group_id=db_tags_group.id, general_account_id=general_account_id
    )
    return TagsGroupRead.from_orm(new_tags_group)


async def list_tags_groups(
    general_account_id: UUID = Depends(get_current_general_account_id),
    db: AsyncSession = Depends(get_db),
) -> List[TagsGroupRead]:
    """
    Lists all tags groups for the authenticated user's general account.
    """
    repo = TagsGroupRepository(db)
    tags_groups = await repo.list_tags_groups_by_general_account_id(general_account_id)
    return [TagsGroupRead.from_orm(tg) for tg in tags_groups]


async def get_tags_group(
    tags_group_id: UUID,
    general_account_id: UUID = Depends(get_current_general_account_id),
    db: AsyncSession = Depends(get_db),
) -> TagsGroupRead:
    """
    Retrieves a single tags group by its ID, verifying ownership.
    """
    repo = TagsGroupRepository(db)
    tags_group = await repo.get_tags_group_by_id(tags_group_id, general_account_id)

    if not tags_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tags Group not found or access denied.",
        )
    return TagsGroupRead.from_orm(tags_group)


async def update_tags_group(
    tags_group_id: UUID,
    tags_group_data: TagsGroupUpdate,
    general_account_id: UUID = Depends(get_current_general_account_id),
    db: AsyncSession = Depends(get_db),
) -> TagsGroupRead:
    """
    Updates a tags group, verifying ownership.
    """
    repo = TagsGroupRepository(db)
    tags_group_to_update = await repo.get_tags_group_by_id(
        tags_group_id, general_account_id
    )

    if not tags_group_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tags Group not found or access denied.",
        )

    # Update the object
    await repo.update_tags_group(
        db_obj=tags_group_to_update, tags_group_data=tags_group_data
    )
    # Commit the changes
    await db.commit()
    # Re-fetch the updated object with relationships
    updated_group = await repo.get_tags_group_by_id(
        tags_group_id=tags_group_id, general_account_id=general_account_id
    )
    return TagsGroupRead.from_orm(updated_group)


async def delete_tags_group(
    tags_group_id: UUID,
    general_account_id: UUID = Depends(get_current_general_account_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Deletes a tags group and all its associated tags, verifying ownership.
    """
    repo = TagsGroupRepository(db)
    tags_group_to_delete = await repo.get_tags_group_by_id(
        tags_group_id, general_account_id
    )

    if not tags_group_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tags Group not found or access denied.",
        )

    await repo.delete_tags_group(db_obj=tags_group_to_delete)
    await db.commit()
    return {"ok": True, "detail": "Tags Group deleted successfully."}


async def reorder_tags_groups(
    reorder_data: TagsGroupReorder,
    general_account_id: UUID = Depends(get_current_general_account_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Reorders the tags groups for the user.
    """
    repo = TagsGroupRepository(db)
    await repo.reorder_groups(
        general_account_id=general_account_id, group_ids=reorder_data.group_ids
    )
    return {"ok": True, "detail": "Groups reordered successfully."}