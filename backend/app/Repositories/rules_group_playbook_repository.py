# app/Repositories/rules_group_playbook_repository.py
from __future__ import annotations

from typing import Optional, Sequence
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.Models.rules_group_playbook import RulesGroupPlaybook
from app.Schemas.rules_group_playbook import RulesGroupCreate, RulesGroupUpdate


class RulesGroupPlaybookRepository:
    """Repository for RulesGroupPlaybook CRUD operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, group_id: UUID) -> Optional[RulesGroupPlaybook]:
        stmt = (
            select(RulesGroupPlaybook)
            .where(RulesGroupPlaybook.id == group_id)
            .options(selectinload(RulesGroupPlaybook.rules)) # Eager load rules
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_by_playbook_id(self, playbook_id: UUID) -> Sequence[RulesGroupPlaybook]:
        stmt = (
            select(RulesGroupPlaybook)
            .where(RulesGroupPlaybook.playbook_id == playbook_id)
            .options(selectinload(RulesGroupPlaybook.rules)) # Eager load rules
            .order_by(RulesGroupPlaybook.created_at.asc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def create(self, group_in: RulesGroupCreate) -> RulesGroupPlaybook:
        db_group = RulesGroupPlaybook(
            **group_in.model_dump(),
        )
        self.db.add(db_group)
        await self.db.commit()
        await self.db.refresh(db_group)
        return await self.get_by_id(db_group.id) # Ricarica per avere le rules

    async def update(self, db_obj: RulesGroupPlaybook, obj_in: RulesGroupUpdate) -> RulesGroupPlaybook:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return await self.get_by_id(db_obj.id) # Ricarica per avere le rules

    async def delete(self, db_obj: RulesGroupPlaybook) -> None:
        await self.db.delete(db_obj)
        await self.db.commit()