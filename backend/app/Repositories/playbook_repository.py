# app/Repositories/playbook_repository.py
from __future__ import annotations
from typing import Optional, Sequence, List, Dict, Any
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select, insert, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from app.Models.playbook import Playbook
from app.Models.general_account import GeneralAccount
from app.Models.rules_group_playbook import RulesGroupPlaybook
from app.Models.rule_playbook import RulePlaybook
from app.Models.trade import Trade
from app.Schemas.playbook import PlaybookCreate, PlaybookUpdate


class PlaybookRepository:
    """Repository for Playbook CRUD operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _check_duplicate_title(self, general_account_id: UUID, title: str, current_playbook_id: Optional[UUID] = None) -> None:
        """Checks for a duplicate playbook title within the same general account."""
        query = select(Playbook).where(
            Playbook.general_account_id == general_account_id,
            Playbook.title == title
        )
        if current_playbook_id:
            query = query.where(Playbook.id != current_playbook_id)

        result = await self.db.execute(query)
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A playbook with this title already exists."
            )

    async def get_by_id(self, playbook_id: UUID) -> Optional[Playbook]:
        stmt = (
            select(Playbook)
            .where(Playbook.id == playbook_id)
            .options(
                selectinload(Playbook.rules_groups)
                .selectinload(RulesGroupPlaybook.rules)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_by_id_with_trades(self, playbook_id: UUID) -> Optional[Playbook]:
        stmt = (
            select(Playbook)
            .where(Playbook.id == playbook_id)
            .options(
                selectinload(Playbook.trades),
                joinedload(Playbook.general_account) # Per il controllo utente
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_by_general_account_id(self, general_account_id: UUID) -> Sequence[Playbook]:
        stmt = (
            select(Playbook)
            .where(Playbook.general_account_id == general_account_id)
            .options(selectinload(Playbook.rules_groups))
            .order_by(Playbook.title.asc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def list_by_general_account_id_with_trades(self, general_account_id: UUID) -> Sequence[Playbook]:
        """
        DEPRECATED: inefficient, loads all trades.
        Use list_playbooks_with_stats instead for overviews.
        """
        stmt = (
            select(Playbook)
            .where(Playbook.general_account_id == general_account_id)
            .options(
                selectinload(Playbook.rules_groups).selectinload(RulesGroupPlaybook.rules).selectinload(RulePlaybook.trades),
                selectinload(Playbook.trades)  # Eager load trades
            )
            .order_by(Playbook.title.asc())
        )
        res = await self.db.execute(stmt)
        return res.unique().scalars().all()

    async def list_playbooks_with_stats(self, general_account_id: UUID) -> List[Dict[str, Any]]:
        """
        Recupera tutti i playbook di un utente con le statistiche aggregate calcolate
        direttamente nel database per la massima efficienza.
        """
        # Subquery per aggregare le statistiche dei trade per ogni playbook
        trade_stats_subquery = (
            select(
                Trade.playbook_id,
                func.count(Trade.id).label("total_trades"),
                func.sum(Trade.p_l).label("total_p_l"),
                func.sum(case((Trade.p_l > 0, 1)), else_=0).label("winning_trades"),
                func.sum(case((Trade.p_l < 0, 1)), else_=0).label("losing_trades"),
                func.sum(case((Trade.p_l > 0, Trade.p_l)), else_=0).label("gross_profit"),
                func.sum(case((Trade.p_l < 0, Trade.p_l)), else_=0).label("gross_loss"),
                func.avg(Trade.r_multiple).label("avg_r_multiple"),
                func.avg(Trade.p_l).label("avg_p_l")
            )
            .where(Trade.playbook_id.isnot(None))
            .group_by(Trade.playbook_id)
            .subquery("trade_stats")
        )

        # Query principale per recuperare i playbook e fare un LEFT JOIN con le statistiche
        stmt = (
            select(
                Playbook,
                trade_stats_subquery.c.total_trades,
                trade_stats_subquery.c.total_p_l,
                trade_stats_subquery.c.winning_trades,
                trade_stats_subquery.c.losing_trades,
                trade_stats_subquery.c.gross_profit,
                trade_stats_subquery.c.gross_loss,
                trade_stats_subquery.c.avg_r_multiple,
                trade_stats_subquery.c.avg_p_l
            )
            .outerjoin(trade_stats_subquery, Playbook.id == trade_stats_subquery.c.playbook_id)
            .where(Playbook.general_account_id == general_account_id)
            .options(
                selectinload(Playbook.rules_groups)
                .selectinload(RulesGroupPlaybook.rules)
            )
            .order_by(Playbook.title.asc())
        )

        result = await self.db.execute(stmt)

        # Processa i risultati per combinare il modello Playbook con le statistiche
        playbooks_with_stats = []
        for row in result.all():
            (playbook, total_trades, total_p_l, winning_trades, losing_trades,
             gross_profit, gross_loss, avg_r_multiple, avg_p_l) = row
            playbooks_with_stats.append({
                "playbook": playbook,
                "stats": {
                    "total_trades": total_trades or 0,
                    "total_p_l": float(total_p_l) if total_p_l is not None else 0.0,
                    "winning_trades": winning_trades or 0,
                    "losing_trades": losing_trades or 0,
                    "gross_profit": float(gross_profit) if gross_profit is not None else 0.0,
                    "gross_loss": float(abs(gross_loss)) if gross_loss is not None else 0.0,
                    "avg_r_multiple": float(avg_r_multiple) if avg_r_multiple is not None else 0.0,
                    "avg_p_l": float(avg_p_l) if avg_p_l is not None else 0.0
                }
            })

        return playbooks_with_stats

    async def create(self, playbook_in: PlaybookCreate, general_account_id: UUID) -> Playbook:
        await self._check_duplicate_title(general_account_id, playbook_in.title)

        db_playbook = Playbook(
            **playbook_in.model_dump(),
            general_account_id=general_account_id
        )
        self.db.add(db_playbook)
        await self.db.commit()
        await self.db.refresh(db_playbook)
        # Ricarica l'oggetto con le relazioni per essere sicuri che siano caricate
        return await self.get_by_id(db_playbook.id)

    async def update(self, db_obj: Playbook, obj_in: PlaybookUpdate) -> Playbook:
        update_data = obj_in.model_dump(exclude_unset=True)

        if 'title' in update_data and update_data['title'] != db_obj.title:
            await self._check_duplicate_title(db_obj.general_account_id, update_data['title'], db_obj.id)

        for field, value in update_data.items():
            setattr(db_obj, field, value)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return await self.get_by_id(db_obj.id)

    async def delete(self, db_obj: Playbook) -> None:
        await self.db.delete(db_obj)
        await self.db.commit()

    async def get_analytics_by_playbook_id(self, playbook_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Calcola le metriche analitiche e la curva di equità per un singolo playbook
        utilizzando una query SQL aggregata e funzioni finestra.
        """
        # CTE per ottenere i trade ordinati per un playbook specifico
        trades_cte = (
            select(
                Trade.p_l,
                Trade.r_multiple,
                Trade.exit_timestamp,
                Trade.entry_timestamp,
                # Calcola il P&L cumulativo usando una funzione finestra
                func.sum(Trade.p_l).over(
                    order_by=(func.coalesce(Trade.exit_timestamp, Trade.entry_timestamp))
                ).label("cumulative_pnl")
            )
            .where(Trade.playbook_id == playbook_id, Trade.p_l.isnot(None))
            .cte("trades_data")
        )

        # Query principale per aggregare le metriche e raccogliere i dati della curva di equità
        stmt = (
            select(
                # Metriche aggregate
                func.sum(trades_cte.c.p_l).label("net_pnl"),
                func.count(trades_cte.c.p_l).label("trades_count"),
                func.sum(case((trades_cte.c.p_l > 0, 1)), else_=0).label("winning_trades"),
                func.sum(case((trades_cte.c.p_l < 0, 1)), else_=0).label("losing_trades"),
                func.sum(case((trades_cte.c.p_l > 0, trades_cte.c.p_l)), else_=0).label("gross_profit"),
                func.sum(case((trades_cte.c.p_l < 0, trades_cte.c.p_l)), else_=0).label("gross_loss"),
                func.max(trades_cte.c.p_l).label("largest_profit"),
                func.min(trades_cte.c.p_l).label("largest_loss"),
                func.sum(trades_cte.c.r_multiple).label("total_r_multiple"),

                # Dati per la curva di equità (aggregati come array)
                func.json_agg(
                    func.json_build_object(
                        'date', func.coalesce(trades_cte.c.exit_timestamp, trades_cte.c.entry_timestamp),
                        'cumulative_pnl', trades_cte.c.cumulative_pnl
                    )
                ).label("equity_curve_data")
            )
            .select_from(trades_cte)
        )
        from sqlalchemy.dialects import postgresql
        compiled_stmt = stmt.compile(dialect=postgresql.dialect())
        print("--- BEGIN SQL QUERY ---")
        print(compiled_stmt.string)
        print("--- END SQL QUERY ---")

        result = await self.db.execute(stmt)
        stats = result.first()

        if not stats or stats.trades_count == 0:
            return None

        return dict(stats._asdict())

    async def upsert_by_title(self, general_account_id: UUID, title: str) -> Playbook:
        stmt = select(Playbook).where(Playbook.general_account_id == general_account_id, Playbook.title == title).limit(1)
        res = await self.db.execute(stmt)
        row = res.scalars().first()
        if row:
            return row

        # La descrizione è NOT NULL, quindi forniamo un default vuoto
        stmt_ins = insert(Playbook).values(
            general_account_id=general_account_id,
            title=title,
            description=""
        ).returning(Playbook.id)
        res_ins = await self.db.execute(stmt_ins)
        new_id = res_ins.scalar_one()
        await self.db.commit()
        return await self.get_by_id(new_id)

    async def list_all_playbooks_grouped_by_account(self) -> Sequence[GeneralAccount]:
        """
        Lista tutti i GeneralAccount con i loro playbook e utenti associati.
        Utile per l'endpoint admin.
        """
        stmt = (
            select(GeneralAccount)
            .options(
                joinedload(GeneralAccount.user),
                selectinload(GeneralAccount.playbooks).selectinload(Playbook.rules_groups)
            )
            .order_by(GeneralAccount.created_at.asc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().unique().all()