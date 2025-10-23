# app/Repositories/rules_group_playbook_repository.py
from __future__ import annotations

from typing import Optional, Sequence, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.Models.rule_playbook import RulePlaybook
from app.Models.rules_group_playbook import RulesGroupPlaybook
from app.Schemas.rules_group_playbook import RulesGroupCreate, RulesGroupUpdate
from app.Repositories.rule_playbook_repository import RulePlaybookRepository
from app.Schemas.rule_playbook import RuleMetrics


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

    async def get_by_playbook_id(self, playbook_id: UUID) -> Sequence[RulesGroupPlaybook]:
        stmt = (
            select(RulesGroupPlaybook)
            .where(RulesGroupPlaybook.playbook_id == playbook_id)
            .order_by(RulesGroupPlaybook.order.asc(), RulesGroupPlaybook.created_at.asc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def list_by_playbook_id_inefficient(self, playbook_id: UUID) -> Sequence[RulesGroupPlaybook]:
        """ DEPRECATED: This method is inefficient as it loads all trades for all rules. """
        stmt = (
            select(RulesGroupPlaybook)
            .where(RulesGroupPlaybook.playbook_id == playbook_id)
            .options(
                selectinload(RulesGroupPlaybook.rules)
                .selectinload(RulePlaybook.trades)
            )
            .order_by(RulesGroupPlaybook.order.asc(), RulesGroupPlaybook.created_at.asc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().unique().all()

    async def list_groups_with_rule_stats_by_playbook_id(self, playbook_id: UUID) -> Sequence[RulesGroupPlaybook]:
        """
        Efficiently lists rule groups for a playbook and attaches aggregated
        statistics to each rule without loading all trades into memory.
        """
        # Step 1: Fetch groups and their rules (without trades)
        stmt = (
            select(RulesGroupPlaybook)
            .where(RulesGroupPlaybook.playbook_id == playbook_id)
            .options(selectinload(RulesGroupPlaybook.rules))
            .order_by(RulesGroupPlaybook.order.asc(), RulesGroupPlaybook.created_at.asc())
        )
        res = await self.db.execute(stmt)
        groups = res.scalars().unique().all()

        if not groups:
            return []

        # Step 2: Get stats for all rules in the playbook in a single query
        rule_repo = RulePlaybookRepository(self.db)
        rule_stats_map = await rule_repo.get_stats_for_rules_in_playbooks([playbook_id])

        # Step 3: Attach stats to the rules in the fetched groups
        for group in groups:
            for rule in group.rules:
                stats = rule_stats_map.get(rule.id)
                if stats:
                    rule.metrics = RuleMetrics(**stats)
                else:
                    rule.metrics = RuleMetrics(follow_rate=0, net_pnl=0, win_rate=0, profit_factor=None)

        return groups

    async def bulk_update_order(self, group_ids: List[UUID]) -> None:
        """
        Updates the 'order' field for a list of rule groups in a single transaction.
        """
        for index, group_id in enumerate(group_ids):
            stmt = select(RulesGroupPlaybook).where(RulesGroupPlaybook.id == group_id)
            result = await self.db.execute(stmt)
            group = result.scalars().first()
            if group:
                group.order = index
        await self.db.commit()

    async def create(self, group_in: RulesGroupCreate) -> RulesGroupPlaybook:
        db_group = RulesGroupPlaybook(
            **group_in.model_dump(),
        )
        self.db.add(db_group)
        await self.db.commit()
        await self.db.refresh(db_group)
        return await self.get_by_id(db_group.id) # Ricarica per avere le rules

    async def create_with_playbook_id(self, obj_in: dict, playbook_id: UUID) -> RulesGroupPlaybook:
        # Rimuovi 'id' se presente, perché è per un nuovo oggetto
        obj_in.pop('id', None)
        # Le regole vengono gestite separatamente dal controller
        obj_in.pop('rules', None)
        db_group = RulesGroupPlaybook(**obj_in, playbook_id=playbook_id)
        self.db.add(db_group)
        await self.db.commit()
        await self.db.refresh(db_group)
        return db_group

    async def update(self, db_obj: RulesGroupPlaybook, obj_in: dict) -> RulesGroupPlaybook:
        # Rimuovi 'id' e 'rules' che non devono essere aggiornati direttamente
        obj_in.pop('id', None)
        obj_in.pop('rules', None)
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: RulesGroupPlaybook) -> None:
        await self.db.delete(db_obj)
        await self.db.commit()

    async def delete_by_id(self, group_id: UUID) -> None:
        db_obj = await self.get_by_id(group_id)
        if db_obj:
            await self.delete(db_obj)