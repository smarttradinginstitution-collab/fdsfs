# app/Services/analytics_service.py
from __future__ import annotations

from uuid import UUID
from datetime import date, datetime, timezone
from typing import List, Dict, Optional, Any
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np

from app.Infrastructure.db import get_db
from app.Repositories.trade_repository import TradeRepository
from app.Schemas.analytics import (
    PerformanceMetrics,
    PerformanceStats,
    CalendarDayData,
    ProcessedStats,
    VantageScoreData,
    EquityCurveData,
    StrategyPerformance,
    DayOfWeekPerformance,
    WinLossDays,
    TradeSummary
)

class AnalyticsService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
        self.trade_repo = TradeRepository(db)

    async def get_performance_metrics(
        self,
        trading_account_id: UUID,
        start_date: date,
        end_date: date
    ) -> PerformanceMetrics:
        trades = await self.trade_repo.get_filtered_trades(trading_account_id, start_date, end_date)

        if not trades:
            return PerformanceMetrics(stats=PerformanceStats())

        net_pnl = sum(trade.p_l for trade in trades if trade.p_l is not None)
        trade_count = len(trades)

        winning_trades_list = [t for t in trades if t.p_l is not None and t.p_l > 0]
        losing_trades_list = [t for t in trades if t.p_l is not None and t.p_l < 0]

        winning_trades_count = len(winning_trades_list)
        losing_trades_count = len(losing_trades_list)

        win_rate = (winning_trades_count / trade_count) * 100 if trade_count > 0 else 0

        gross_profit = sum(t.p_l for t in winning_trades_list)
        gross_loss = abs(sum(t.p_l for t in losing_trades_list))

        avg_win = gross_profit / winning_trades_count if winning_trades_count > 0 else 0
        avg_loss = gross_loss / losing_trades_count if losing_trades_count > 0 else 0

        profit_factor = gross_profit / gross_loss if gross_loss > 0 else None
        profit_factor_label = f"{profit_factor:.2f}" if profit_factor is not None else "∞"

        stats = PerformanceStats(
            net_pnl=net_pnl,
            gross_profit=gross_profit,
            gross_loss=gross_loss,
            win_rate=win_rate,
            trade_count=trade_count,
            winning_trades=winning_trades_count,
            losing_trades=losing_trades_count,
            breakeven_trades=trade_count - winning_trades_count - losing_trades_count,
            profit_factor=profit_factor,
            profit_factor_label=profit_factor_label,
            avg_win=avg_win,
            avg_loss=avg_loss,
            largest_profit=max((t.p_l for t in trades if t.p_l is not None), default=0),
            largest_loss=min((t.p_l for t in trades if t.p_l is not None), default=0),
        )

        return PerformanceMetrics(stats=stats)

    async def get_calendar_data(
        self,
        trading_account_id: UUID,
        start_date: date,
        end_date: date,
        user_timezone: str # Non ancora utilizzato, ma pronto per il futuro
    ) -> List[CalendarDayData]:
        trades = await self.trade_repo.get_filtered_trades(trading_account_id, start_date, end_date)

        daily_summary = {}
        for trade in trades:
            if trade.entry_timestamp:
                trade_date = trade.entry_timestamp.date()
                if trade_date not in daily_summary:
                    daily_summary[trade_date] = {"pnl": 0, "trade_count": 0, "winning_trades_count": 0}

                daily_summary[trade_date]["pnl"] += trade.p_l or 0
                daily_summary[trade_date]["trade_count"] += 1
                if trade.p_l and trade.p_l > 0:
                    daily_summary[trade_date]["winning_trades_count"] += 1

        return [
            CalendarDayData(
                date=day,
                pnl=data["pnl"],
                trade_count=data["trade_count"],
                winning_trades_count=data["winning_trades_count"]
            ) for day, data in daily_summary.items()
        ]

    async def get_processed_stats(
        self,
        trading_account_id: UUID,
        start_date: date,
        end_date: date
    ) -> ProcessedStats:
        # Logica Mock per ora, per sbloccare il frontend
        return ProcessedStats(
            by_strategy={},
            max_abs_pnl_by_strategy=0,
            by_day_of_week={},
            win_loss_days=WinLossDays(winningDays=0, losingDays=0, breakEvenDays=0),
            monthly_totals={},
            weekly_totals={}
        )

    async def get_vantage_score(
        self,
        trading_account_id: UUID,
        start_date: date,
        end_date: date
    ) -> VantageScoreData:
        # Logica Mock
        return VantageScoreData(
            vantage_score=0,
            win_rate_score=0,
            profit_factor_score=0,
            avg_win_loss_score=0,
            recovery_factor_score=0,
            max_drawdown_score=0,
            consistency_score=0
        )

    async def get_equity_curve(
        self,
        trading_account_id: UUID,
        start_date: date,
        end_date: date
    ) -> EquityCurveData:
        """
        Calcola i dati per la curva di equity (P&L cumulativo) in un dato periodo.
        """
        trades = await self.trade_repo.get_filtered_trades(trading_account_id, start_date, end_date)
        if not trades:
            return EquityCurveData(labels=[], data=[])

        # Ordina i trade per data di chiusura (o apertura se non chiusi)
        sorted_trades = sorted(trades, key=lambda t: t.exit_timestamp or t.entry_timestamp)

        labels = []
        cumulative_pnl_data = []
        cumulative_pnl = 0

        for trade in sorted_trades:
            if trade.p_l is not None:
                cumulative_pnl += trade.p_l
                trade_date = (trade.exit_timestamp or trade.entry_timestamp).date()
                labels.append(trade_date)
                cumulative_pnl_data.append(cumulative_pnl)

        return EquityCurveData(labels=labels, data=cumulative_pnl_data)

    async def get_trade_summary(
        self,
        trading_account_id: UUID,
        start_date: date,
        end_date: date
    ) -> TradeSummary:
        """
        Recupera un riepilogo completo dei trade per un dato periodo.
        """
        performance_metrics = await self.get_performance_metrics(trading_account_id, start_date, end_date)
        equity_curve = await self.get_equity_curve(trading_account_id, start_date, end_date)

        return TradeSummary(
            stats=performance_metrics.stats,
            cumulative_pnl_series=equity_curve
        )