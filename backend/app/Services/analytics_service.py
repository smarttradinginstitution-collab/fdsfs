# app/Services/analytics_service.py
from __future__ import annotations
from uuid import UUID
from datetime import date
from typing import List, Dict, Any
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Repositories.trade_repository import TradeRepository
from app.Repositories.trading_account_repository import TradingAccountRepository
from app.Services.metrics.metrics_calculator import MetricsCalculator
from app.Schemas.analytics import (
    PerformanceMetrics,
    PerformanceStats,
    CalendarDayData,
    ProcessedStats,
    VantageScoreData,
    EquityCurveData,
    StrategyPerformance,
    WinLossDays,
    TradeSummary,
    DailySummary
)
from app.Schemas.trade import TradeRead

class AnalyticsService:
    """
    Service layer for handling analytics requests.
    Acts as an orchestrator that fetches data and uses MetricsCalculator for calculations.
    """
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
        self.trade_repo = TradeRepository(db)
        self.trading_account_repo = TradingAccountRepository(db)

    async def _get_calculator(self, trading_account_id: UUID, start_date: date, end_date: date) -> MetricsCalculator:
        """Helper method to get trades and instantiate the calculator."""
        trades = await self.trade_repo.get_filtered_trades(trading_account_id, start_date, end_date)
        trading_account = await self.trading_account_repo.get_by_id(trading_account_id)

        initial_balance = trading_account.initial_balance if trading_account else 0.0

        return MetricsCalculator(trades, initial_balance)

    async def get_performance_metrics(
        self, trading_account_id: UUID, start_date: date, end_date: date
    ) -> PerformanceMetrics:
        """
        Calculates and returns main performance metrics.
        """
        calculator = await self._get_calculator(trading_account_id, start_date, end_date)
        all_metrics = calculator.get_all_metrics()

        # Map calculator results to the PerformanceStats Pydantic schema
        stats = PerformanceStats(
            net_pnl=all_metrics["net_pnl"],
            roi_percentage=all_metrics["roi_percentage"],
            gross_profit=all_metrics["gross_profit"],
            gross_loss=all_metrics["gross_loss"],
            win_rate=all_metrics["win_rate"],
            trade_count=all_metrics["trade_count"],
            winning_trades=all_metrics["winning_trades"],
            losing_trades=all_metrics["losing_trades"],
            breakeven_trades=all_metrics["breakeven_trades"],
            profit_factor=all_metrics["profit_factor"],
            profit_factor_label=all_metrics["profit_factor_label"],
            avg_win=all_metrics["avg_win"],
            avg_loss=all_metrics["avg_loss"],
            largest_profit=all_metrics["largest_profit"],
            largest_loss=all_metrics["largest_loss"],
            max_consecutive_wins=all_metrics["max_consecutive_wins"],
            max_consecutive_losses=all_metrics["max_consecutive_losses"],
            average_hold_time=all_metrics["average_hold_time"],
            expectancy=all_metrics["expectancy"],
            average_trade_pnl=all_metrics["average_trade_pnl"],
            avg_realized_rr=all_metrics["avg_realized_rr"],
            max_drawdown_abs=all_metrics["max_drawdown_abs"],
            max_drawdown_percentage=all_metrics["max_drawdown_percentage"],
            sharpe_ratio=all_metrics["sharpe_ratio"]
        )
        return PerformanceMetrics(stats=stats)

    async def get_calendar_data(
        self, trading_account_id: UUID, start_date: date, end_date: date, user_timezone: str
    ) -> List[CalendarDayData]:
        """
        Returns data aggregated by day for the calendar view.
        """
        calculator = await self._get_calculator(trading_account_id, start_date, end_date)
        calendar_data = calculator.calculate_calendar_data()

        return [CalendarDayData(**item) for item in calendar_data]

    async def get_processed_stats(
        self, trading_account_id: UUID, start_date: date, end_date: date
    ) -> ProcessedStats:
        """
        Returns aggregated stats like 'by_strategy', 'by_day_of_week', etc.
        """
        calculator = await self._get_calculator(trading_account_id, start_date, end_date)
        processed_data = calculator.calculate_processed_stats()

        # Map the nested dictionary to the required Pydantic models
        return ProcessedStats(
            by_strategy={
                name: StrategyPerformance(**data)
                for name, data in processed_data["by_strategy"].items()
            },
            max_abs_pnl_by_strategy=processed_data["max_abs_pnl_by_strategy"],
            by_day_of_week=processed_data["by_day_of_week"],
            win_loss_days=WinLossDays(**processed_data["win_loss_days"]),
            monthly_totals=processed_data["monthly_totals"],
            weekly_totals=processed_data["weekly_totals"]
        )

    async def get_vantage_score(
        self, trading_account_id: UUID, start_date: date, end_date: date
    ) -> VantageScoreData:
        """
        Calculates and returns the Vantage Score and its components.
        This logic remains here as it's a specific interpretation of the base metrics.
        """
        calculator = await self._get_calculator(trading_account_id, start_date, end_date)
        metrics = calculator.get_all_metrics()

        if metrics["trade_count"] < 5:
            return VantageScoreData(vantage_score=0, win_rate_score=0, profit_factor_score=0,
                                    avg_win_loss_score=0, recovery_factor_score=0,
                                    max_drawdown_score=0, consistency_score=0)

        def normalize(value, min_val, max_val, invert=False):
            f_value = float(value)
            f_min_val = float(min_val)
            f_max_val = float(max_val)

            f_value = max(f_min_val, min(f_value, f_max_val))
            denominator = f_max_val - f_min_val
            if denominator == 0: return 0.0
            score = ((f_value - f_min_val) / denominator) * 100.0
            return 100.0 - score if invert else score

        win_rate_score = normalize(metrics["win_rate"], 0, 100)
        profit_factor_score = normalize(metrics["profit_factor"] or 0, 0, 5)
        avg_win_loss_ratio = (metrics["avg_win"] / metrics["avg_loss"]) if metrics["avg_loss"] > 0 else Decimal('5.0')
        avg_win_loss_score = normalize(avg_win_loss_ratio, 0, 5)
        recovery_factor = (float(metrics["net_pnl"]) / metrics["max_drawdown_abs"]) if metrics["max_drawdown_abs"] > 0 else 0.0
        recovery_factor_score = normalize(recovery_factor, 0, 10)

        # Use the new max_drawdown_percentage from the calculator
        max_drawdown_score = normalize(metrics["max_drawdown_percentage"], 0, 100, invert=True)

        consistency_score = normalize(metrics["sharpe_ratio"], -1, 2)

        scores = [win_rate_score, profit_factor_score, avg_win_loss_score, recovery_factor_score, max_drawdown_score, consistency_score]
        final_score = sum(scores) / len(scores)

        return VantageScoreData(
            vantage_score=int(final_score),
            win_rate_score=int(win_rate_score),
            profit_factor_score=int(profit_factor_score),
            avg_win_loss_score=int(avg_win_loss_score),
            recovery_factor_score=int(recovery_factor_score),
            max_drawdown_score=int(max_drawdown_score),
            consistency_score=int(consistency_score)
        )

    async def get_equity_curve(
        self, trading_account_id: UUID, start_date: date, end_date: date
    ) -> EquityCurveData:
        """
        Returns data for the equity curve chart.
        """
        calculator = await self._get_calculator(trading_account_id, start_date, end_date)
        equity_curve_data = calculator.calculate_equity_curve()
        return EquityCurveData(**equity_curve_data)

    async def get_trade_summary(
        self, trading_account_id: UUID, start_date: date, end_date: date
    ) -> TradeSummary:
        """
        Returns a complete summary of trades for a given period.
        """
        # We can call the other methods in this service to build the summary
        performance_metrics = await self.get_performance_metrics(trading_account_id, start_date, end_date)
        equity_curve = await self.get_equity_curve(trading_account_id, start_date, end_date)

        return TradeSummary(
            stats=performance_metrics.stats,
            cumulative_pnl_series=equity_curve
        )

    async def get_daily_summary(
        self, trading_account_id: UUID, day: date
    ) -> DailySummary:
        """
        Returns a complete summary for a single day, including stats,
        chart data, and the list of trades.
        """
        # Re-use the existing helper to get a calculator scoped to the specific day
        calculator = await self._get_calculator(trading_account_id, day, day)

        # Get all base metrics from the calculator
        all_metrics = calculator.get_all_metrics()
        stats = PerformanceStats(**all_metrics)

        # Get the equity curve for the day
        equity_curve_data = calculator.calculate_equity_curve()
        equity_curve = EquityCurveData(**equity_curve_data)

        # Get the list of trades for the day
        trades_for_day = [TradeRead.from_orm(trade) for trade in calculator.trades]

        return DailySummary(
            stats=stats,
            cumulative_pnl_series=equity_curve,
            trades=trades_for_day
        )