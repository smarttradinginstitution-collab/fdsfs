# app/Services/tag_service.py
from __future__ import annotations
from uuid import UUID
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status

from app.Infrastructure.db import get_db
from app.Repositories.tag_repository import TagRepository
from app.Schemas.tag import TagCreate, TagUpdate
from app.Models.tag import Tag


class TagService:
    def __init__(
        self,
        db: AsyncSession = Depends(get_db),
    ):
        self.db = db
        self.repo = TagRepository(db)

    async def create_tag(self, tag_data: TagCreate) -> Tag:
        return await self.repo.create_tag(tag_data=tag_data)

    async def get_tag_by_id(self, tag_id: UUID) -> Tag:
        db_obj = await self.repo.get_tag_by_id(tag_id=tag_id)
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
            )
        return db_obj

    async def list_tags_by_group_id(self, group_id: UUID) -> List[Tag]:
        return await self.repo.list_by_group_id(group_id=group_id)

    async def update_tag(self, db_obj: Tag, tag_data: TagUpdate) -> Tag:
        return await self.repo.update(db_obj=db_obj, data=tag_data)

    async def delete_tag(self, db_obj: Tag) -> None:
        return await self.repo.delete(db_obj=db_obj)
