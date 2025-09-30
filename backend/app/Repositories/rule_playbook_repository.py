# app/Repositories/rule_playbook_repository.py
from __future__ import annotations

from typing import Optional, Sequence, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.rule_playbook import RulePlaybook
from app.Models.rules_group_playbook import RulesGroupPlaybook
from app.Schemas.rule_playbook import RuleCreate, RuleUpdate


class RulePlaybookRepository:
    """Repository for RulePlaybook CRUD operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, rule_id: UUID) -> Optional[RulePlaybook]:
        stmt = select(RulePlaybook).where(RulePlaybook.id == rule_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_by_group_id(self, group_id: UUID) -> Sequence[RulePlaybook]:
        stmt = (
            select(RulePlaybook)
            .where(RulePlaybook.rules_groups_playbook_id == group_id)
            .order_by(RulePlaybook.created_at.asc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def get_by_ids_and_playbook_id(self, rule_ids: List[UUID], playbook_id: UUID) -> Sequence[RulePlaybook]:
        """
        Recupera una lista di regole tramite i loro ID, assicurandosi che appartengano
        al playbook specificato.
        """
        if not rule_ids:
            return []

        stmt = (
            select(RulePlaybook)
            .join(RulesGroupPlaybook)
            .where(
                RulePlaybook.id.in_(rule_ids),
                RulesGroupPlaybook.playbook_id == playbook_id
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create(self, rule_in: RuleCreate) -> RulePlaybook:
        db_rule = RulePlaybook(
            **rule_in.model_dump(),
        )
        self.db.add(db_rule)
        await self.db.commit()
        await self.db.refresh(db_rule)
        return db_rule

    async def update(self, db_obj: RulePlaybook, obj_in: RuleUpdate) -> RulePlaybook:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: RulePlaybook) -> None:
        await self.db.delete(db_obj)
        await self.db.commit()