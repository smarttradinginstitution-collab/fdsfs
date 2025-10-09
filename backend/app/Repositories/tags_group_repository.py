# app/Repositories/tags_group_repository.py
from __future__ import annotations

from typing import Optional, Sequence, List
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.tags_group import TagsGroup
from app.Schemas.tags_group import TagsGroupCreate, TagsGroupUpdate


class TagsGroupRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_tags_group(
        self, tags_group_data: TagsGroupCreate, general_account_id: UUID
    ) -> TagsGroup:
        """
        Crea un nuovo gruppo di tag, assicurandosi che il nome sia unico
        all'interno del general_account.
        """
        # Verifica l'esistenza di un gruppo con lo stesso nome (case-insensitive)
        stmt = select(TagsGroup).where(
            func.lower(TagsGroup.name) == tags_group_data.name.lower(),
            TagsGroup.general_account_id == general_account_id,
        )
        existing_group = await self.db.execute(stmt)
        if existing_group.scalars().first():
            raise HTTPException(
                status_code=409,
                detail="A tags group with this name already exists.",
            )

        # Se non esiste, crea il nuovo gruppo
        db_tags_group = TagsGroup(
            **tags_group_data.model_dump(), general_account_id=general_account_id
        )
        self.db.add(db_tags_group)
        await self.db.commit()
        await self.db.refresh(db_tags_group)
        return db_tags_group

    async def get_tags_group_by_id(
        self, tags_group_id: UUID, general_account_id: UUID
    ) -> Optional[TagsGroup]:
        """Retrieves a specific tags group by ID for a given general account."""
        stmt = (
            select(TagsGroup)
            .where(
                TagsGroup.id == tags_group_id,
                TagsGroup.general_account_id == general_account_id,
            )
            .limit(1)
        )
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def list_tags_groups_by_general_account_id(
        self, general_account_id: UUID
    ) -> Sequence[TagsGroup]:
        """Lists all tags groups for a given general_account_id."""
        stmt = (
            select(TagsGroup)
            .where(TagsGroup.general_account_id == general_account_id)
            .order_by(TagsGroup.position.asc(), TagsGroup.name.asc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def update_tags_group(
        self, db_obj: TagsGroup, tags_group_data: TagsGroupUpdate
    ) -> TagsGroup:
        """Updates an existing tags group."""
        update_data = tags_group_data.model_dump(exclude_unset=True)
        if not update_data:
            return db_obj

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete_tags_group(self, db_obj: TagsGroup) -> None:
        """Deletes a tags group."""
        await self.db.delete(db_obj)
        await self.db.commit()

    async def reorder_groups(
        self, general_account_id: UUID, group_ids: List[UUID]
    ) -> None:
        """
        Updates the position of multiple tags groups in a single transaction.
        """
        for index, group_id in enumerate(group_ids):
            stmt = (
                select(TagsGroup)
                .where(
                    TagsGroup.id == group_id,
                    TagsGroup.general_account_id == general_account_id,
                )
            )
            result = await self.db.execute(stmt)
            group = result.scalars().first()
            if group:
                group.position = index

        await self.db.commit()