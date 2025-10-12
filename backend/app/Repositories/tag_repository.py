from __future__ import annotations

from typing import Optional, Sequence
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, insert, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload, contains_eager

from app.Models.tag import Tag
from app.Models.general_account import GeneralAccount
from app.Models.auth_user import AuthUser
from app.Schemas.tag import TagCreate, TagUpdate


class TagRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_tag_by_id(self, tag_id: UUID) -> Optional[Tag]:
        """Recupera un tag specifico per ID."""
        stmt = select(Tag).where(Tag.id == tag_id).options(joinedload(Tag.group)).limit(1)
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def create_tag(self, tag_data: TagCreate) -> Tag:
        """Crea un nuovo tag, assicurandosi che il nome sia unico all'interno del gruppo."""
        stmt = select(Tag).where(
            Tag.name == tag_data.name,
            Tag.group_id == tag_data.group_id
        )
        existing_tag = await self.db.execute(stmt)
        if existing_tag.scalars().first():
            raise HTTPException(
                status_code=409,
                detail="A tag with this name already exists in this group.",
            )

        db_tag = Tag(**tag_data.model_dump())
        self.db.add(db_tag)
        # The commit will be handled by the service layer.
        return db_tag

    async def update_tag(self, db_obj: Tag, tag_data: TagUpdate) -> Tag:
        """Aggiorna un tag esistente."""
        update_data = tag_data.model_dump(exclude_unset=True)
        if not update_data:
            return db_obj

        if "name" in update_data and update_data["name"] != db_obj.name:
            stmt = select(Tag).where(
                Tag.name == update_data["name"],
                Tag.group_id == db_obj.group_id,
                Tag.id != db_obj.id,
            )
            existing_tag = await self.db.execute(stmt)
            if existing_tag.scalars().first():
                raise HTTPException(
                    status_code=409,
                    detail="A tag with this name already exists in this group.",
                )

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete_tag(self, db_obj: Tag) -> None:
        """Elimina un tag."""
        await self.db.delete(db_obj)
        await self.db.commit()

    async def list_tags_by_general_account_id(self, general_account_id: UUID) -> Sequence[Tag]:
        """Lists all tags for a given general_account_id by joining through TagsGroup."""
        from app.Models.tags_group import TagsGroup
        stmt = (
            select(Tag)
            .join(TagsGroup, Tag.group_id == TagsGroup.id)
            .where(TagsGroup.general_account_id == general_account_id)
            .order_by(Tag.name.asc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def upsert_by_name(self, general_account_id: UUID, name: str, color: Optional[str] = None) -> Tag:
        from app.Models.tags_group import TagsGroup

        # 1. Find or create a default group for the general account
        group_stmt = select(TagsGroup).where(
            TagsGroup.general_account_id == general_account_id,
            TagsGroup.name == "Default"
        ).limit(1)
        res_group = await self.db.execute(group_stmt)
        group = res_group.scalars().first()

        if not group:
            group = TagsGroup(
                general_account_id=general_account_id,
                name="Default",
                description="Default group for tags created on the fly."
            )
            self.db.add(group)
            await self.db.flush()
            await self.db.refresh(group)

        # 2. Find tag by name within that group
        tag_stmt = select(Tag).where(Tag.group_id == group.id, Tag.name == name).limit(1)
        res_tag = await self.db.execute(tag_stmt)
        tag = res_tag.scalars().first()

        if tag:
            if color and tag.color != color:
                tag.color = color
                self.db.add(tag)
                await self.db.commit()
                await self.db.refresh(tag)
            return tag

        # 3. Create tag if it does not exist
        new_tag = Tag(name=name, color=color, group_id=group.id)
        self.db.add(new_tag)
        await self.db.commit()

        # Re-fetch the tag to ensure the group relationship is loaded, preventing lazy-load errors.
        created_tag = await self.get_tag_by_id(new_tag.id)
        return created_tag