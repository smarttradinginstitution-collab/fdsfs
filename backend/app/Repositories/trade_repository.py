# app/Repositories/trade_repository.py
from __future__ import annotations

from uuid import UUID
from typing import List, Optional
from datetime import date, datetime, timedelta

import pytz
from sqlalchemy.orm import joinedload
from sqlalchemy import select, func, case, cast, Date, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.trade import Trade, TradeDirectionEnum
from app.Schemas.trade import TradeCreate, TradeUpdate
from app.Schemas.stats import (
    TradeSummary,
    PerformanceMetrics,
    CalendarData,
    ProcessedStats,
    EquityCurveData,
)
from app.Schemas.vantage_score import VantageScoreData


class TradeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _get_trade_query(self):
        """Costruisce la query base per i trade con tutte le relazioni pre-caricate."""
        return (
            select(Trade)
            .options(
                joinedload(Trade.tags),
                joinedload(Trade.mistakes),
                joinedload(Trade.playbooks),
                joinedload(Trade.news_impacts),
                joinedload(Trade.psychology_states),
                joinedload(Trade.asset),
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
        return result.scalars().first()

    async def list_by_trading_account_id(
        self, trading_account_id: UUID
    ) -> List[Trade]:
        """Elenca tutti i trade per un dato trading account."""
        query = self._get_trade_query().where(Trade.trading_account_id == trading_account_id)
        result = await self.db.execute(query)
        return result.unique().scalars().all()

    async def get_trade_by_id_simple(self, trade_id: UUID) -> Optional[Trade]:
        """Recupera un trade per ID senza controlli di appartenenza."""
        query = self._get_trade_query().where(Trade.id == trade_id)
        result = await self.db.execute(query)
        return result.scalars().first()

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

    async def delete_trade(self, db_trade: Trade) -> None:
        """Elimina un trade."""
        await self.db.delete(db_trade)
        await self.db.commit()

    # ==============================================================================
    # METODI PER STATISTICHE E DASHBOARD
    # ==============================================================================

    def _get_filtered_trades_query(
        self,
        trading_account_id: UUID,
        start_date: date,
        end_date: date,
        setups: Optional[List[str]] = None,
    ):
        """
        Crea una query base per i trade filtrata per trading account, intervallo di date
        e, opzionalmente, per setup/playbook.
        """
        from app.Models.playbook import Playbook # Import locale per evitare dipendenze circolari

        query = select(Trade).where(
            Trade.trading_account_id == trading_account_id,
            cast(Trade.entry_timestamp, Date) >= start_date,
            cast(Trade.entry_timestamp, Date) <= end_date,
        )

        if setups:
            query = query.join(Trade.playbooks).where(Playbook.title.in_(setups))

        return query

    async def get_performance_metrics(
        self,
        trading_account_id: UUID,
        start_date: date,
        end_date: date,
        setups: Optional[List[str]] = None,
    ) -> PerformanceMetrics:
        """Calcola e ritorna un oggetto con tutte le metriche di performance aggregate."""

        trades_query = self._get_filtered_trades_query(
            trading_account_id, start_date, end_date, setups
        ).subquery()

        winning_trades_count = func.sum(case((trades_query.c.p_l > 0, 1), else_=0)).label("winning_trades_count")
        losing_trades_count = func.sum(case((trades_query.c.p_l < 0, 1), else_=0)).label("losing_trades_count")
        breakeven_trades_count = func.sum(case((trades_query.c.p_l == 0, 1), else_=0)).label("breakeven_trades_count")

        total_wins = func.sum(case((trades_query.c.p_l > 0, trades_query.c.p_l), else_=0)).label("total_wins")
        total_losses = func.sum(case((trades_query.c.p_l < 0, trades_query.c.p_l), else_=0)).label("total_losses")

        trade_count = func.count(trades_query.c.id).label("trade_count")

        stats_query = select(
            trade_count,
            func.sum(trades_query.c.p_l).label("total_pl"),
            winning_trades_count,
            losing_trades_count,
            breakeven_trades_count,
            total_wins,
            total_losses,
            func.max(trades_query.c.p_l).label("largest_profit"),
            func.min(trades_query.c.p_l).label("largest_loss"),
        ).select_from(trades_query)

        result = await self.db.execute(stats_query)
        stats = result.first()

        if not stats or stats.trade_count == 0:
            return PerformanceMetrics() # Ritorna metriche di default

        win_rate = (stats.winning_trades_count / stats.trade_count) * 100 if stats.trade_count else 0
        avg_win = stats.total_wins / stats.winning_trades_count if stats.winning_trades_count else 0
        avg_loss = abs(stats.total_losses / stats.losing_trades_count) if stats.losing_trades_count else 0
        profit_factor_val = stats.total_wins / abs(stats.total_losses) if stats.total_losses != 0 else float('inf')
        expectancy = (win_rate / 100 * avg_win) - ((1 - win_rate / 100) * avg_loss)

        return PerformanceMetrics(
            trade_count=stats.trade_count or 0,
            total_pl=stats.total_pl or 0.0,
            winning_trades_count=stats.winning_trades_count or 0,
            losing_trades_count=stats.losing_trades_count or 0,
            breakeven_trades_count=stats.breakeven_trades_count or 0,
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor_val,
            expectancy=expectancy,
            largest_profit=stats.largest_profit or 0.0,
            largest_loss=stats.largest_loss or 0.0,
            avg_trade_pnl= (stats.total_pl / stats.trade_count) if stats.trade_count else 0,
            max_consecutive_wins=0,
            max_consecutive_losses=0,
            avg_realized_rr=0,
            max_drawdown_abs=0,
            sharpe_ratio=0,
            average_hold_time=0,
        )

    async def get_calendar_data(
        self,
        trading_account_id: UUID,
        start_date: date,
        end_date: date,
        user_timezone: str,
        setups: Optional[List[str]] = None,
    ) -> List[CalendarData]:
        """Aggrega i dati dei trade per giorno per la heatmap del calendario."""

        trades_query = self._get_filtered_trades_query(
            trading_account_id, start_date, end_date, setups
        ).subquery()

        entry_date_in_user_tz = func.timezone(user_timezone, trades_query.c.entry_timestamp)
        date_col = cast(entry_date_in_user_tz, Date).label("date")

        query = (
            select(
                date_col,
                func.sum(trades_query.c.p_l).label("pnl"),
                func.count(trades_query.c.id).label("trade_count"),
                func.sum(case((trades_query.c.p_l > 0, 1), else_=0)).label("winning_trades_count"),
            )
            .select_from(trades_query)
            .group_by(date_col)
            .order_by(date_col)
        )

        result = await self.db.execute(query)
        rows = result.all()

        return [
            CalendarData(
                date=row.date,
                pnl=row.pnl or 0.0,
                trade_count=row.trade_count or 0,
                winning_trades_count=row.winning_trades_count or 0,
            )
            for row in rows
        ]

    async def get_equity_curve(
        self,
        trading_account_id: UUID,
        start_date: date,
        end_date: date,
        setups: Optional[List[str]] = None,
    ) -> EquityCurveData:
        """Calcola i dati per la curva di equity."""

        trades_query = self._get_filtered_trades_query(
            trading_account_id, start_date, end_date, setups
        )

        ordered_trades_query = trades_query.order_by(
            func.coalesce(Trade.exit_timestamp, Trade.entry_timestamp)
        )

        result = await self.db.execute(ordered_trades_query)
        trades = result.scalars().all()

        cumulative_pnl = 0.0
        labels = [start_date.strftime("%Y-%m-%d")]
        data = [0.0]

        for trade in trades:
            cumulative_pnl += trade.p_l or 0
            timestamp = trade.exit_timestamp or trade.entry_timestamp
            data.append(cumulative_pnl)
            labels.append(timestamp.strftime("%Y-%m-%d"))

        return EquityCurveData(labels=labels, data=data)

    async def get_trade_summary(
        self, trading_account_id: UUID, start_date: date, end_date: date, user_timezone: str, setups: Optional[List[str]]
    ) -> TradeSummary:
        """Fornisce un riepilogo dei trade e delle statistiche per un intervallo."""
        # This is a placeholder implementation. A full implementation would likely
        # combine get_performance_metrics and list_by_trading_account_id.
        return TradeSummary(stats={}, trades=[], cumulative_pnl_series={})

    async def get_processed_stats(
        self, trading_account_id: UUID, start_date: date, end_date: date, setups: Optional[List[str]]
    ) -> ProcessedStats:
        # Placeholder
        return ProcessedStats()

    async def get_vantage_score(
        self, trading_account_id: UUID, start_date: date, end_date: date, setups: Optional[List[str]]
    ) -> VantageScoreData:
        # Placeholder
        return VantageScoreData()