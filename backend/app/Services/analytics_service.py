# app/Services/analytics_service.py
from __future__ import annotations
from decimal import Decimal

from uuid import UUID
from datetime import date
from typing import List
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Repositories.trade_repository import TradeRepository
from app.Services.metrics.metrics_calculator import MetricsCalculator
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

        calculator = MetricsCalculator(trades)
        metrics = calculator.calculate_all_metrics()
        stats = metrics['stats']

        # Mappatura da dizionario a Pydantic Model
        performance_stats = PerformanceStats(
            net_pnl=stats.get('total_pl', 0),
            gross_profit=sum(pnl for pnl in stats.get('pnl_data', []) if pnl > 0),
            gross_loss=abs(sum(pnl for pnl in stats.get('pnl_data', []) if pnl < 0)),
            win_rate=stats.get('win_rate', 0),
            trade_count=stats.get('trade_count', 0),
            winning_trades=stats.get('winning_trades_count', 0),
            losing_trades=stats.get('losing_trades_count', 0),
            breakeven_trades=stats.get('breakeven_trades_count', 0),
            profit_factor=stats.get('profit_factor'),
            profit_factor_label=stats.get('profit_factor_label'),
            avg_win=stats.get('avg_win'),
            avg_loss=stats.get('avg_loss'),
            largest_profit=stats.get('largest_profit'),
            largest_loss=stats.get('largest_loss'),
            max_consecutive_wins=stats.get('max_consecutive_wins'),
            max_consecutive_losses=stats.get('max_consecutive_losses'),
            average_hold_time=stats.get('average_hold_time'),
            expectancy=stats.get('expectancy'),
            average_trade_pnl=stats.get('average_trade_pnl'),
            avg_realized_rr=stats.get('avg_realized_rr'),
            max_drawdown_abs=stats.get('max_drawdown_abs'),
            sharpe_ratio=stats.get('sharpe_ratio')
        )

        return PerformanceMetrics(stats=performance_stats)

    async def get_calendar_data(
        self,
        trading_account_id: UUID,
        start_date: date,
        end_date: date,
        user_timezone: str
    ) -> List[CalendarDayData]:
        trades = await self.trade_repo.get_filtered_trades(trading_account_id, start_date, end_date)
        if not trades:
            return []

        calculator = MetricsCalculator(trades, user_timezone=user_timezone)
        processed_stats = calculator.calculate_processed_stats()
        daily_data = processed_stats.get('daily_data', {})

        return [
            CalendarDayData(
                date=day,
                pnl=data.get('total_pnl', 0),
                trade_count=data.get('trade_count', 0),
                winning_trades_count=data.get('winning_trades', 0)
            ) for day, data in daily_data.items()
        ]

    async def get_processed_stats(
        self,
        trading_account_id: UUID,
        start_date: date,
        end_date: date
    ) -> ProcessedStats:
        trades = await self.trade_repo.get_filtered_trades(trading_account_id, start_date, end_date)
        if not trades:
            return ProcessedStats()

        calculator = MetricsCalculator(trades)
        stats = calculator.calculate_processed_stats()

        # Mappatura da dizionario a Pydantic Model
        by_strategy_performance = {
            name: StrategyPerformance(
                trade_count=data.get('trade_count', 0),
                total_pnl=data.get('total_pnl', 0.0),
                win_rate=data.get('win_rate', 0.0)
            ) for name, data in stats.get('by_strategy', {}).items()
        }

        win_loss_data = stats.get('win_loss_days', {})
        win_loss_days = WinLossDays(
            winningDays=win_loss_data.get('winning_days', 0),
            losingDays=win_loss_data.get('losing_days', 0),
            breakEvenDays=win_loss_data.get('breakeven_days', 0)
        )

        by_day_of_week_performance = {
            name: DayOfWeekPerformance(**data)
            for name, data in stats.get('by_day_of_week', {}).items()
        }

        return ProcessedStats(
            by_strategy=by_strategy_performance,
            max_abs_pnl_by_strategy=stats.get('max_abs_pnl_by_strategy', 0.0),
            by_day_of_week=by_day_of_week_performance,
            win_loss_days=win_loss_days,
            monthly_totals=stats.get('monthly_totals', {}),
            weekly_totals=stats.get('weekly_totals', {})
        )

    async def get_vantage_score(
        self,
        trading_account_id: UUID,
        start_date: date,
        end_date: date
    ) -> VantageScoreData:
        trades = await self.trade_repo.get_filtered_trades(trading_account_id, start_date, end_date)
        if not trades or len(trades) < 5:
             return VantageScoreData(
                vantage_score=0, win_rate_score=0, profit_factor_score=0,
                avg_win_loss_score=0, recovery_factor_score=0,
                max_drawdown_score=0, consistency_score=0
            )

        calculator = MetricsCalculator(trades)
        vantage_scores = calculator.calculate_vantage_score()

        return VantageScoreData(
            vantage_score=vantage_scores.get('vantage_score', 0),
            win_rate_score=vantage_scores.get('win_rate_score', 0),
            profit_factor_score=vantage_scores.get('profit_factor_score', 0),
            avg_win_loss_score=vantage_scores.get('avg_win_loss_score', 0),
            recovery_factor_score=vantage_scores.get('recovery_factor_score', 0),
            max_drawdown_score=vantage_scores.get('max_drawdown_score', 0),
            consistency_score=vantage_scores.get('consistency_score', 0)
        )

    async def get_equity_curve(
        self,
        trading_account_id: UUID,
        start_date: date,
        end_date: date
    ) -> EquityCurveData:
        trades = await self.trade_repo.get_filtered_trades(trading_account_id, start_date, end_date)
        if not trades:
            return EquityCurveData(labels=[], data=[])

        calculator = MetricsCalculator(trades)
        equity_curve_data = calculator.calculate_equity_curve()

        # Convert date objects to strings for labels if they aren't already
        labels = [
            label.strftime('%Y-%m-%d') if isinstance(label, date) else label
            for label in equity_curve_data.get('labels', [])
        ]

        return EquityCurveData(
            labels=labels,
            data=[float(d) for d in equity_curve_data.get('data', [])]
        )

    async def get_trade_summary(
        self,
        trading_account_id: UUID,
        start_date: date,
        end_date: date
    ) -> TradeSummary:
        trades = await self.trade_repo.get_filtered_trades(trading_account_id, start_date, end_date)
        if not trades:
            return TradeSummary(
                stats=PerformanceStats(),
                cumulative_pnl_series=EquityCurveData(labels=[], data=[])
            )

        calculator = MetricsCalculator(trades)
        summary = calculator.calculate_trade_summary()

        stats_data = summary.get('stats', {})

        # Gestione di 'inf' per profit_factor
        profit_factor = stats_data.get('profit_factor')
        if profit_factor == float('inf'):
            profit_factor = None # O un valore numerico elevato se preferito

        performance_stats = PerformanceStats(
            net_pnl=stats_data.get('net_pnl', 0),
            gross_profit=stats_data.get('gross_profit', 0),
            gross_loss=stats_data.get('gross_loss', 0),
            win_rate=stats_data.get('win_rate', 0),
            trade_count=stats_data.get('trade_count', 0),
            winning_trades=stats_data.get('winning_trades', 0),
            losing_trades=stats_data.get('losing_trades', 0),
            breakeven_trades=stats_data.get('breakeven_trades', 0),
            profit_factor=profit_factor,
            profit_factor_label=stats_data.get('profit_factor_label', "0.00"),
            avg_win=stats_data.get('avg_win', 0),
            avg_loss=stats_data.get('avg_loss', 0)
        )

        equity_curve_data = summary.get('cumulative_pnl_series', {'labels': [], 'data': []})

        return TradeSummary(
            stats=performance_stats,
            cumulative_pnl_series=EquityCurveData(**equity_curve_data)
        )