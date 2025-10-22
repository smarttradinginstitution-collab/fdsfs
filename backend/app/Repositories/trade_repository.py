# app/Repositories/trade_repository.py
from __future__ import annotations

from uuid import UUID
from typing import List, Optional, Any
from datetime import date
from collections import defaultdict
from decimal import Decimal
import datetime
import json

from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy import select, func, case, Float
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.trade import Trade
from app.Models.tag import Tag
from app.Models.trades_tags import TradesTags
from app.Models.trading_account import TradingAccount
from app.Schemas.trade import TradeCreate, TradeUpdate
from app.Models.rule_playbook import RulePlaybook
from app.Models.playbook import Playbook


class TradeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _get_trade_query(self):
        """Costruisce la query base per i trade con tutte le relazioni pre-caricate."""

        # Calcola la durata in minuti direttamente nel database
        duration_minutes = case(
            (
                Trade.exit_timestamp.isnot(None) & Trade.entry_timestamp.isnot(None),
                func.extract('epoch', Trade.exit_timestamp - Trade.entry_timestamp) / 60
            ),
            else_=None
        ).label('duration_minutes')

        return (
            select(Trade, duration_minutes)
            .options(
                selectinload(Trade.tags).joinedload(Tag.group),
                selectinload(Trade.mistakes),
                joinedload(Trade.playbook),
                selectinload(Trade.news_impacts),
                selectinload(Trade.psychology_states),
                joinedload(Trade.asset),
                selectinload(Trade.rules_followed),
                # Eager load the trading account to access initial_balance for ROI calculation
                joinedload(Trade.trading_account),
            )
        )

    async def get_by_id(
        self, trade_id: UUID, trading_account_id: UUID
    ) -> Optional[Trade]:
        """Recupera un trade per ID, assicurandosi che appartenga al trading account corretto."""
        query = self._get_trade_query().where(
            Trade.id == trade_id,
            Trade.trading_account_id == trading_account_id
        )
        result = await self.db.execute(query)
        row = result.unique().first()
        if row:
            trade, duration = row
            trade.duration_minutes = duration
            return trade
        return None

    async def get_by_id_and_general_account(
        self, trade_id: UUID, general_account_id: UUID
    ) -> Optional[Trade]:
        """Recupera un trade per ID, assicurandosi che appartenga al general account corretto."""
        query = (
            self._get_trade_query()
            .join(Trade.trading_account)
            .where(
                Trade.id == trade_id,
                TradingAccount.general_account_id == general_account_id,
            )
        )
        result = await self.db.execute(query)
        row = result.unique().first()
        if row:
            trade, duration = row
            trade.duration_minutes = duration
            return trade
        return None

    async def list_by_trading_account_id(
        self, trading_account_id: UUID
    ) -> List[Trade]:
        """Elenca tutti i trade per un dato trading account."""
        query = self._get_trade_query().where(Trade.trading_account_id == trading_account_id)
        result = await self.db.execute(query)
        rows = result.unique().all()
        trades = []
        for trade, duration in rows:
            trade.duration_minutes = duration
            trades.append(trade)
        return trades

    async def get_trades_for_dna_analysis(
        self,
        general_account_id: UUID,
        tag_ids: Optional[List[UUID]] = None,
        mistake_ids: Optional[List[UUID]] = None,
        psychology_state_ids: Optional[List[UUID]] = None,
        news_impact_ids: Optional[List[UUID]] = None,
    ) -> List[Trade]:
        """
        Fetches trades for a general account, dynamically filtering by any combination
        of provided label IDs.
        """
        from app.Models.trades_tags import TradesTags
        from app.Models.trades_mistakes import TradesMistakes
        from app.Models.trades_psychology import TradesPsychology
        from app.Models.trades_news_impacts import TradesNewsImpacts

        query = self._get_trade_query().join(Trade.trading_account).where(
            TradingAccount.general_account_id == general_account_id
        )

        if tag_ids:
            query = query.join(
                TradesTags.__table__, Trade.id == TradesTags.__table__.c.trade_id
            ).where(TradesTags.__table__.c.tag_id.in_(tag_ids))

        if mistake_ids:
            query = query.join(
                TradesMistakes.__table__, Trade.id == TradesMistakes.__table__.c.trade_id
            ).where(TradesMistakes.__table__.c.mistake_id.in_(mistake_ids))

        if psychology_state_ids:
            query = query.join(
                TradesPsychology.__table__, Trade.id == TradesPsychology.__table__.c.trade_id
            ).where(TradesPsychology.__table__.c.psychology_id.in_(psychology_state_ids))

        if news_impact_ids:
            query = query.join(
                TradesNewsImpacts.__table__, Trade.id == TradesNewsImpacts.__table__.c.trade_id
            ).where(TradesNewsImpacts.__table__.c.news_impact_id.in_(news_impact_ids))

        result = await self.db.execute(query)
        rows = result.unique().all()
        trades = []
        for trade, duration in rows:
            trade.duration_minutes = duration
            trades.append(trade)
        return trades

    async def list_by_playbook_id(self, playbook_id: UUID) -> List[Trade]:
        """Elenca tutti i trade per un dato playbook."""
        query = self._get_trade_query().where(Trade.playbook_id == playbook_id)
        result = await self.db.execute(query)
        rows = result.unique().all()
        trades = []
        for trade, duration in rows:
            trade.duration_minutes = duration
            trades.append(trade)
        return trades

    async def list_recent_by_general_account_id(
        self, general_account_id: UUID, limit: int = 20
    ) -> List[tuple[Trade, bool]]:
        """
        Lists the most recent trades for a given general account,
        and includes a boolean indicating if each trade is linked to a note.
        """
        from app.Models.note import Note
        from sqlalchemy import exists

        # Correlated subquery to check if a note exists for the trade.
        has_note_subquery = (
            select(Note.id).where(Note.trade_id == Trade.id).exists()
        ).label("is_linked_to_note")

        # We get the base query which now returns (Trade, duration_minutes)
        base_query = self._get_trade_query()

        # We create a subquery from the base query to be able to select from it
        subq = base_query.subquery()

        # We need to reconstruct the select to include the new subquery
        # while keeping the original columns from the base query.
        query = (
            select(Trade, has_note_subquery, subq.c.duration_minutes)
            .select_from(subq) # Select from the subquery
            .join(Trade, subq.c.id == Trade.id) # Join the Trade model back to get the object
            .options(
                selectinload(Trade.tags).joinedload(Tag.group),
                joinedload(Trade.mistakes),
                joinedload(Trade.playbook),
                joinedload(Trade.news_impacts),
                joinedload(Trade.psychology_states),
                joinedload(Trade.asset),
                selectinload(Trade.rules_followed),
                joinedload(Trade.trading_account),
            )
            .join(Trade.trading_account)
            .where(TradingAccount.general_account_id == general_account_id)
            .order_by(Trade.entry_timestamp.desc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        rows = result.unique().all()

        trades_with_note_status = []
        for trade, has_note, duration in rows:
            trade.duration_minutes = duration
            trades_with_note_status.append((trade, has_note))

        return trades_with_note_status

    async def get_filtered_trades(
        self,
        trading_account_id: UUID,
        start_date: date,
        end_date: date
    ) -> List[Trade]:
        """Recupera i trade filtrati per un intervallo di date, includendo l'intero giorno di fine."""
        from datetime import datetime, time

        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)

        query = self._get_trade_query().where(
            Trade.trading_account_id == trading_account_id,
            Trade.entry_timestamp >= start_datetime,
            Trade.entry_timestamp <= end_datetime
        )
        result = await self.db.execute(query)
        rows = result.unique().all()
        trades = []
        for trade, duration in rows:
            trade.duration_minutes = duration
            trades.append(trade)
        return trades

    async def get_trade_by_id_simple(self, trade_id: UUID) -> Optional[Trade]:
        """Recupera un trade per ID senza controlli di appartenenza."""
        query = self._get_trade_query().where(Trade.id == trade_id)
        result = await self.db.execute(query)
        row = result.first()
        if row:
            trade, duration = row
            trade.duration_minutes = duration
            return trade
        return None

    async def get_trade_for_details_view(self, trade_id: UUID) -> Optional[Trade]:
        """
        Recupera un trade per ID, caricando esplicitamente tutte le relazioni e i campi
        necessari per la vista dettagliata e i calcoli delle metriche.
        Questo previene problemi di lazy-loading con la sessione asincrona.
        """
        query = self._get_trade_query().where(Trade.id == trade_id)
        result = await self.db.execute(query)
        row = result.first()
        if row:
            trade, duration = row
            trade.duration_minutes = duration
            return trade
        return None

    async def add_and_commit(self, db_trade: Trade) -> Trade:
        """Aggiunge, committa e refresha un'istanza di trade."""
        self.db.add(db_trade)
        await self.db.commit()
        await self.db.refresh(db_trade)
        return db_trade

    async def commit_and_refresh(self, db_trade: Trade) -> Trade:
        """Committa le modifiche e refresha l'istanza."""
        await self.db.commit()
        await self.db.refresh(db_trade)
        return db_trade

    async def update_review_status(self, trade: Trade, is_reviewed: bool) -> Trade:
        """Aggiorna lo stato di revisione di un trade."""
        trade.is_reviewed = is_reviewed
        # Il service layer gestirà il commit e il refresh.
        return trade

    async def delete_trade(self, db_trade: Trade) -> None:
        """Elimina un trade."""
        await self.db.delete(db_trade)
        await self.db.commit()

    async def update_trade_rules(self, trade: Trade, rule_ids: list[UUID]):
        """
        Aggiorna le regole 'seguite' per un trade specifico.
        Sostituisce completamente le regole esistenti con la nuova lista.
        """
        # Carica le istanze complete delle regole per assicurarsi che esistano
        rules_result = await self.db.execute(
            select(RulePlaybook).where(RulePlaybook.id.in_(rule_ids))
        )
        rules = rules_result.scalars().all()

        # Verifica che tutti gli ID richiesti corrispondano a regole esistenti
        if len(rules) != len(rule_ids):
            raise ValueError("Una o più Rule ID non sono valide.")

        # Sostituisci la lista delle regole associate al trade
        trade.rules_followed = rules

        # Il commit verrà gestito dal service layer

    async def get_aggregated_performance_stats(
        self,
        trading_account_id: UUID,
        start_date: date,
        end_date: date,
    ) -> dict[str, Any]:
        """
        Calcola le metriche di performance aggregate direttamente nel database per la massima efficienza.
        """
        from datetime import datetime, time
        from sqlalchemy import cast, Numeric

        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)

        # Filtri comuni per le query
        filters = [
            Trade.trading_account_id == trading_account_id,
            Trade.entry_timestamp >= start_datetime,
            Trade.entry_timestamp <= end_datetime,
            Trade.p_l.isnot(None)
        ]

        # Definizioni delle aggregazioni
        query_aggs = [
            func.sum(Trade.p_l).label("net_pnl"),
            func.count(Trade.id).label("trade_count"),
            func.count(case((Trade.p_l > 0, 1))).label("winning_trades"),
            func.count(case((Trade.p_l < 0, 1))).label("losing_trades"),
            func.sum(case((Trade.p_l > 0, Trade.p_l), else_=0)).label("gross_profit"),
            func.sum(case((Trade.p_l < 0, Trade.p_l), else_=0)).label("gross_loss"),
            func.max(Trade.p_l).label("largest_profit"),
            func.min(Trade.p_l).label("largest_loss"),
            func.avg(Trade.r_multiple).label("avg_realized_rr")
        ]

        stmt = select(*query_aggs).where(*filters)

        result = await self.db.execute(stmt)
        stats = result.mappings().first()

        # Se non ci sono trade, restituisce una struttura dati vuota/default
        if not stats or stats['trade_count'] == 0:
            return {
                "net_pnl": 0.0, "trade_count": 0, "winning_trades": 0, "losing_trades": 0,
                "breakeven_trades": 0, "gross_profit": 0.0, "gross_loss": 0.0,
                "avg_win": 0.0, "avg_loss": 0.0, "largest_profit": 0.0, "largest_loss": 0.0,
                "avg_realized_rr": 0.0,
            }

        # Post-elaborazione dei risultati per calcolare medie e valori derivati
        win_count = stats['winning_trades'] or 0
        loss_count = stats['losing_trades'] or 0
        total_count = stats['trade_count'] or 0

        processed_stats = {
            "net_pnl": float(stats['net_pnl'] or 0.0),
            "trade_count": total_count,
            "winning_trades": win_count,
            "losing_trades": loss_count,
            "breakeven_trades": total_count - (win_count + loss_count),
            "gross_profit": float(stats['gross_profit'] or 0.0),
            "gross_loss": abs(float(stats['gross_loss'] or 0.0)),
            "avg_win": (float(stats['gross_profit']) / win_count) if win_count > 0 else 0.0,
            "avg_loss": abs(float(stats['gross_loss']) / loss_count) if loss_count > 0 else 0.0,
            "largest_profit": float(stats['largest_profit'] or 0.0),
            "largest_loss": float(stats['largest_loss'] or 0.0),
            "avg_realized_rr": float(stats['avg_realized_rr'] or 0.0),
        }

        return processed_stats

    async def get_calendar_data_aggregated(
        self,
        trading_account_id: UUID,
        start_date: date,
        end_date: date,
    ) -> list[dict[str, Any]]:
        """
        Calcola i dati aggregati per la vista calendario direttamente nel database.
        """
        from datetime import datetime, time

        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)

        trade_date_col = func.date(Trade.entry_timestamp).label("date")

        stmt = (
            select(
                trade_date_col,
                func.sum(Trade.p_l).label("pnl"),
                func.count(Trade.id).label("trade_count"),
                func.count(case((Trade.p_l > 0, 1))).label("winning_trades_count"),
            )
            .where(
                Trade.trading_account_id == trading_account_id,
                Trade.entry_timestamp >= start_datetime,
                Trade.entry_timestamp <= end_datetime,
                Trade.p_l.isnot(None),
            )
            .group_by(trade_date_col)
            .order_by(trade_date_col)
        )

        result = await self.db.execute(stmt)
        # Restituisce una lista di dizionari, facile da mappare in Pydantic
        return result.mappings().all()

    async def get_equity_curve_aggregated(
        self,
        trading_account_id: UUID,
        start_date: date,
        end_date: date,
    ) -> list[dict[str, Any]]:
        """
        Calcola i punti della curva di equità usando le Window Functions di SQL.
        """
        from datetime import datetime, time

        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)

        # Subquery per ordinare i trade e calcolare il P&L cumulativo
        subquery = (
            select(
                Trade.entry_timestamp.label("timestamp"),
                func.sum(Trade.p_l).over(
                    order_by=Trade.entry_timestamp
                ).label("cumulative_pnl")
            )
            .where(
                Trade.trading_account_id == trading_account_id,
                Trade.entry_timestamp >= start_datetime,
                Trade.entry_timestamp <= end_datetime,
                Trade.p_l.isnot(None)
            )
            .subquery()
        )

        # Query principale per selezionare i dati dalla subquery
        stmt = select(
            subquery.c.timestamp.label("label"),
            subquery.c.cumulative_pnl.label("value")
        ).order_by(subquery.c.timestamp)

        result = await self.db.execute(stmt)
        return result.mappings().all()

    async def get_tag_performance_stats(
        self,
        trading_account_id: UUID,
        start_date: date,
        end_date: date,
    ) -> List[Any]:
        """
        Calcola le statistiche di performance per ogni tag in un dato periodo.
        """
        from datetime import datetime, time

        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)

        # Define aggregate functions
        total_pnl = func.sum(Trade.p_l).label("total_pnl")
        total_trades = func.count(Trade.id).label("total_trades")

        # Calculate win rate safely, avoiding division by zero
        winning_trades = func.count(case((Trade.p_l > 0, 1)))
        win_rate = case(
            (total_trades > 0, (winning_trades.cast(Float) * 100 / total_trades)),
            else_=0.0
        ).label("win_rate")

        # Calculate average R-Multiple, handling NULLs and defaulting to 0
        avg_r_multiple = func.coalesce(func.avg(Trade.r_multiple), 0.0).label("avg_r_multiple")

        stmt = (
            select(
                Tag.id.label("tag_id"),
                Tag.name.label("tag_name"),
                Tag.color.label("tag_color"),
                total_pnl,
                total_trades,
                win_rate,
                avg_r_multiple,
            )
            .select_from(Tag)
            .join(TradesTags.__table__, Tag.id == TradesTags.__table__.c.tag_id)
            .join(Trade, Trade.id == TradesTags.__table__.c.trade_id)
            .where(
                Trade.trading_account_id == trading_account_id,
                Trade.entry_timestamp >= start_datetime,
                Trade.entry_timestamp <= end_datetime,
            )
            .group_by(Tag.id, Tag.name, Tag.color)
            .order_by(total_pnl.desc())
        )

        result = await self.db.execute(stmt)
        return result.all()

    async def get_processed_stats_aggregated(
        self,
        trading_account_id: UUID,
        start_date: date,
        end_date: date,
    ) -> dict[str, Any]:
        """
        Calcola tutte le statistiche aggregate per l'endpoint processed-stats, utilizzando
        una query ottimizzata per PostgreSQL in produzione e un fallback per SQLite nei test.
        """
        # Determina il dialetto del DB per decidere quale implementazione usare
        dialect = self.db.bind.dialect.name

        # Implementazione ottimizzata per PostgreSQL
        if dialect == 'postgresql':
            from sqlalchemy import text
            from datetime import timedelta

            # Calcola la data di fine inclusiva in Python per evitare logica complessa in SQL
            end_date_inclusive = end_date + timedelta(days=1)

            sql_query = text("""
                WITH trades_in_range AS (
                    SELECT
                        t.p_l,
                        t.entry_timestamp,
                        p.title AS strategy_name,
                        EXTRACT(isodow FROM t.entry_timestamp) AS day_of_week,
                        DATE(t.entry_timestamp) AS trade_date
                    FROM trades t
                    LEFT JOIN playbooks p ON t.playbook_id = p.id
                    WHERE t.trading_account_id = :trading_account_id
                      AND t.entry_timestamp >= :start_date
                      AND t.entry_timestamp < :end_date_inclusive
                      AND t.p_l IS NOT NULL
                ),
                strategy_stats AS (
                    SELECT json_object_agg(strategy_name, json_build_object('trade_count', trade_count, 'total_pnl', total_pnl, 'winning_trades', winning_trades)) AS by_strategy
                    FROM (SELECT strategy_name, count(*) AS trade_count, sum(p_l) AS total_pnl, count(*) FILTER (WHERE p_l > 0) AS winning_trades FROM trades_in_range WHERE strategy_name IS NOT NULL GROUP BY strategy_name) AS s
                ),
                day_of_week_stats AS (
                    SELECT json_object_agg(day_of_week, json_build_object('trade_count', trade_count, 'total_pnl', total_pnl)) AS by_day_of_week
                    FROM (SELECT day_of_week, count(*) AS trade_count, sum(p_l) AS total_pnl FROM trades_in_range GROUP BY day_of_week) AS d
                ),
                daily_pnl_stats AS (
                    SELECT json_object_agg(trade_date, daily_pnl) AS daily_pnl
                    FROM (SELECT trade_date, sum(p_l) AS daily_pnl FROM trades_in_range GROUP BY trade_date) AS dp
                )
                SELECT (SELECT by_strategy FROM strategy_stats), (SELECT by_day_of_week FROM day_of_week_stats), (SELECT daily_pnl FROM daily_pnl_stats);
            """)
            result = await self.db.execute(sql_query, {
                "trading_account_id": trading_account_id,
                "start_date": start_date,
                "end_date_inclusive": end_date_inclusive
            })
            raw_results = result.first()

            by_strategy_data = raw_results[0] if raw_results and raw_results[0] is not None else {}
            by_day_of_week_data = {int(k): v for k, v in raw_results[1].items()} if raw_results and raw_results[1] is not None else {}
            daily_pnl_data = raw_results[2] if raw_results and raw_results[2] is not None else {}

            return {"by_strategy": by_strategy_data, "by_day_of_week": by_day_of_week_data, "daily_pnl": daily_pnl_data}

        # Fallback per SQLite (usato nei test)
        else:
            base_query = (
                select(Trade.p_l, Trade.entry_timestamp, Playbook.title.label("strategy_name"))
                .outerjoin(Playbook, Trade.playbook_id == Playbook.id)
                .where(
                    Trade.trading_account_id == trading_account_id,
                    Trade.entry_timestamp >= datetime.datetime.combine(start_date, datetime.time.min),
                    Trade.entry_timestamp <= datetime.datetime.combine(end_date, datetime.time.max),
                    Trade.p_l.isnot(None)
                )
            )
            trades = (await self.db.execute(base_query)).mappings().all()
            if not trades:
                return {"by_strategy": {}, "by_day_of_week": {}, "daily_pnl": {}}

            by_strategy = defaultdict(lambda: {"trade_count": 0, "total_pnl": Decimal("0.0"), "winning_trades": 0})
            by_day_of_week = defaultdict(lambda: {"trade_count": 0, "total_pnl": Decimal("0.0")})
            daily_pnl_agg = defaultdict(lambda: Decimal("0.0"))

            for trade in trades:
                pnl, dt, strategy = trade.p_l, trade.entry_timestamp, trade.strategy_name
                if strategy:
                    by_strategy[strategy]["trade_count"] += 1
                    by_strategy[strategy]["total_pnl"] += pnl
                    if pnl > 0: by_strategy[strategy]["winning_trades"] += 1
                day_index = dt.isoweekday()
                by_day_of_week[day_index]["trade_count"] += 1
                by_day_of_week[day_index]["total_pnl"] += pnl
                daily_pnl_agg[dt.date()] += pnl

            return {
                "by_strategy": {name: dict(data) for name, data in by_strategy.items()},
                "by_day_of_week": {day: dict(data) for day, data in by_day_of_week.items()},
                "daily_pnl": {d.isoformat(): p for d, p in daily_pnl_agg.items()},
            }

    async def get_account_balance(self, trading_account_id: UUID) -> float:
        """
        Calculates the current account balance by taking the initial balance
        and adding the sum of all trade P/L.
        """
        # Get the initial balance
        account_result = await self.db.execute(
            select(TradingAccount.initial_balance).where(TradingAccount.id == trading_account_id)
        )
        initial_balance = account_result.scalar_one_or_none() or 0.0

        # Get the sum of P/L
        pnl_result = await self.db.execute(
            select(func.sum(Trade.p_l)).where(Trade.trading_account_id == trading_account_id)
        )
        total_pnl = pnl_result.scalar_one_or_none() or 0.0

        return float(initial_balance) + float(total_pnl)

    async def get_daily_pnl(self, trading_account_id: UUID, specific_date: date) -> float:
        """Calculates the total P/L for a specific day."""
        from datetime import datetime, time
        start_datetime = datetime.combine(specific_date, time.min)
        end_datetime = datetime.combine(specific_date, time.max)

        pnl_result = await self.db.execute(
            select(func.sum(Trade.p_l)).where(
                Trade.trading_account_id == trading_account_id,
                Trade.entry_timestamp >= start_datetime,
                Trade.entry_timestamp <= end_datetime
            )
        )
        pnl = pnl_result.scalar_one_or_none()
        return float(pnl) if pnl is not None else 0.0

    async def get_trades_with_stop_loss_count(self, trading_account_id: UUID, specific_date: date) -> int:
        """Counts trades with a stop loss for a specific day."""
        from datetime import datetime, time
        start_datetime = datetime.combine(specific_date, time.min)
        end_datetime = datetime.combine(specific_date, time.max)

        count_result = await self.db.execute(
            select(func.count(Trade.id)).where(
                Trade.trading_account_id == trading_account_id,
                Trade.entry_timestamp >= start_datetime,
                Trade.entry_timestamp <= end_datetime,
                Trade.stop_loss_price.isnot(None)
            )
        )
        return count_result.scalar_one()

    async def get_trade_stats_by_day_for_date_range(
        self, trading_account_id: UUID, start_date: date, end_date: date
    ) -> dict[date, dict[str, int]]:
        """
        Calculates trade statistics (total, with stop loss, linked to playbook)
        for each day in a given date range.
        Returns a dictionary mapping dates to their stats.
        """
        from datetime import datetime, time
        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)

        # Use DATE() function to truncate timestamp to date for grouping
        trade_date = func.date(Trade.entry_timestamp).label("trade_date")

        stmt = (
            select(
                trade_date,
                func.count(Trade.id).label("total_trades"),
                func.count(case((Trade.stop_loss_price.isnot(None), Trade.id))).label("trades_with_sl"),
                func.count(case((Trade.playbook_id.isnot(None), Trade.id))).label("trades_linked_to_playbook")
            )
            .where(
                Trade.trading_account_id == trading_account_id,
                Trade.entry_timestamp >= start_datetime,
                Trade.entry_timestamp <= end_datetime
            )
            .group_by(trade_date)
        )

        result = await self.db.execute(stmt)
        stats_by_day = {
            row.trade_date: {
                "total_trades": row.total_trades,
                "trades_with_sl": row.trades_with_sl,
                "trades_linked_to_playbook": row.trades_linked_to_playbook
            }
            for row in result.all()
        }
        return stats_by_day

    async def get_daily_pnl_for_date_range(
        self, trading_account_id: UUID, start_date: date, end_date: date
    ) -> dict[date, float]:
        """
        Calculates the total P/L for each day in a given date range.
        Returns a dictionary mapping dates to their P/L.
        """
        from datetime import datetime, time
        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)

        # Use DATE() function to truncate timestamp to date for grouping
        trade_date = func.date(Trade.entry_timestamp).label("trade_date")

        stmt = (
            select(
                trade_date,
                func.sum(Trade.p_l).label("daily_pnl")
            )
            .where(
                Trade.trading_account_id == trading_account_id,
                Trade.entry_timestamp >= start_datetime,
                Trade.entry_timestamp <= end_datetime
            )
            .group_by(trade_date)
        )

        result = await self.db.execute(stmt)
        pnl_by_day = {row.trade_date: float(row.daily_pnl) for row in result.all()}
        return pnl_by_day

    async def get_trades_linked_to_playbook_count(self, trading_account_id: UUID, specific_date: date) -> int:
        """Counts trades linked to a playbook for a specific day."""
        from datetime import datetime, time
        start_datetime = datetime.combine(specific_date, time.min)
        end_datetime = datetime.combine(specific_date, time.max)

        count_result = await self.db.execute(
            select(func.count(Trade.id)).where(
                Trade.trading_account_id == trading_account_id,
                Trade.entry_timestamp >= start_datetime,
                Trade.entry_timestamp <= end_datetime,
                Trade.playbook_id.isnot(None)
            )
        )
        return count_result.scalar_one()

    async def get_trades_count(self, trading_account_id: UUID, specific_date: date) -> int:
        """Counts total trades for a specific day."""
        from datetime import datetime, time
        start_datetime = datetime.combine(specific_date, time.min)
        end_datetime = datetime.combine(specific_date, time.max)

        count_result = await self.db.execute(
            select(func.count(Trade.id)).where(
                Trade.trading_account_id == trading_account_id,
                Trade.entry_timestamp >= start_datetime,
                Trade.entry_timestamp <= end_datetime
            )
        )
        return count_result.scalar_one()