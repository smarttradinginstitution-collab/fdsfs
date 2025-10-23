# app/Repositories/rule_playbook_repository.py
from __future__ import annotations

from typing import Optional, Sequence, List, Dict, Any
from uuid import UUID
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.Models.rule_playbook import RulePlaybook, trades_rules_association
from app.Models.trade import Trade
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

    async def get_by_group_id(self, group_id: UUID) -> Sequence[RulePlaybook]:
        stmt = (
            select(RulePlaybook)
            .where(RulePlaybook.rules_groups_playbook_id == group_id)
            .order_by(RulePlaybook.order.asc(), RulePlaybook.created_at.asc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def bulk_update_order(self, rule_ids: List[UUID]) -> None:
        """
        Updates the 'order' field for a list of rules in a single transaction.
        """
        for index, rule_id in enumerate(rule_ids):
            stmt = select(RulePlaybook).where(RulePlaybook.id == rule_id)
            result = await self.db.execute(stmt)
            rule = result.scalars().first()
            if rule:
                rule.order = index
        await self.db.commit()

    async def create(self, rule_in: RuleCreate) -> RulePlaybook:
        db_rule = RulePlaybook(
            **rule_in.model_dump(),
        )
        self.db.add(db_rule)
        await self.db.commit()
        await self.db.refresh(db_rule)
        return db_rule

    async def create_with_group_id(self, obj_in: dict, group_id: UUID) -> RulePlaybook:
        obj_in.pop('id', None)
        db_rule = RulePlaybook(**obj_in, rules_groups_playbook_id=group_id)
        self.db.add(db_rule)
        await self.db.commit()
        await self.db.refresh(db_rule)
        return db_rule

    async def update(self, db_obj: RulePlaybook, obj_in: dict) -> RulePlaybook:
        obj_in.pop('id', None)
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: RulePlaybook) -> None:
        await self.db.delete(db_obj)
        await self.db.commit()

    async def delete_by_id(self, rule_id: UUID) -> None:
        db_obj = await self.get_by_id(rule_id)
        if db_obj:
            await self.delete(db_obj)

    async def get_stats_for_rules_in_playbooks(self, playbook_ids: List[UUID]) -> Dict[UUID, Dict[str, Any]]:
        """
        Calcola le statistiche aggregate per tutte le regole dei playbook specificati in una singola query.
        Restituisce un dizionario mappando l'ID di ogni regola alle sue statistiche.
        """
        if not playbook_ids:
            return {}

        # Subquery per contare il totale dei trade per ogni playbook
        total_trades_subquery = (
            select(
                Trade.playbook_id,
                func.count(Trade.id).label("total_playbook_trades")
            )
            .where(Trade.playbook_id.in_(playbook_ids))
            .group_by(Trade.playbook_id)
            .subquery("total_trades_per_playbook")
        )

        # Alias per le tabelle coinvolte per chiarezza
        Rule = aliased(RulePlaybook)
        TradeAssoc = trades_rules_association
        TradeStats = aliased(Trade)
        Group = aliased(RulesGroupPlaybook)

        # Subquery per calcolare le statistiche dei trade per ogni regola
        rule_trade_stats_subquery = (
            select(
                TradeAssoc.c.rule_id.label("rule_id"),
                func.count(TradeStats.id).label("trades_followed_count"),
                func.sum(TradeStats.p_l).label("net_pnl"),
                func.sum(case((TradeStats.p_l > 0, 1)), else_=0).label("winning_trades"),
                func.sum(case((TradeStats.p_l > 0, TradeStats.p_l)), else_=0).label("gross_profit"),
                func.sum(case((TradeStats.p_l < 0, TradeStats.p_l)), else_=0).label("gross_loss")
            )
            .join(TradeStats, TradeAssoc.c.trade_id == TradeStats.id)
            .group_by(TradeAssoc.c.rule_id)
            .subquery("rule_trade_stats")
        )

        # Query principale che unisce le regole con le loro statistiche e il conteggio totale dei trade del playbook
        stmt = (
            select(
                Rule.id,
                Group.playbook_id,
                total_trades_subquery.c.total_playbook_trades,
                rule_trade_stats_subquery.c.trades_followed_count,
                rule_trade_stats_subquery.c.net_pnl,
                rule_trade_stats_subquery.c.winning_trades,
                rule_trade_stats_subquery.c.gross_profit,
                rule_trade_stats_subquery.c.gross_loss
            )
            .join(Group, Rule.rules_groups_playbook_id == Group.id)
            .join(total_trades_subquery, Group.playbook_id == total_trades_subquery.c.playbook_id)
            .outerjoin(rule_trade_stats_subquery, Rule.id == rule_trade_stats_subquery.c.rule_id)
            .where(Group.playbook_id.in_(playbook_ids))
        )

        result = await self.db.execute(stmt)

        # Processa i risultati in un dizionario per un facile accesso
        stats_map = {}
        for row in result.all():
            (rule_id, playbook_id, total_playbook_trades, trades_followed_count,
             net_pnl, winning_trades, gross_profit, gross_loss) = row

            # Inizializza i valori per evitare None
            trades_followed_count = trades_followed_count or 0
            net_pnl = net_pnl or 0
            winning_trades = winning_trades or 0
            gross_profit = gross_profit or 0
            gross_loss = abs(gross_loss) if gross_loss else 0

            # Calcola le metriche derivate
            follow_rate = (trades_followed_count / total_playbook_trades) * 100 if total_playbook_trades > 0 else 0
            win_rate = (winning_trades / trades_followed_count) * 100 if trades_followed_count > 0 else 0
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else None

            stats_map[rule_id] = {
                "follow_rate": follow_rate,
                "net_pnl": float(net_pnl),
                "win_rate": win_rate,
                "profit_factor": profit_factor
            }

        return stats_map