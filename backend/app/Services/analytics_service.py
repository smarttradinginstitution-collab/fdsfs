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
from app.Schemas.analytics import TagPerformanceStat

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
        Calculates and returns main performance metrics using optimized aggregation.
        """
        # 1. Get aggregated stats directly from the database (fast)
        aggregated_stats = await self.trade_repo.get_aggregated_performance_stats(
            trading_account_id, start_date, end_date
        )

        # 2. Get the full list of trades for more complex, in-memory calculations (slower but necessary for now)
        # This is the part we want to optimize further in the future if needed.
        calculator = await self._get_calculator(trading_account_id, start_date, end_date)

        # 3. Calculate complex metrics that are hard to do in pure SQL
        # We pass the pre-aggregated stats to the calculator to avoid re-calculating them.
        complex_metrics = calculator.get_all_metrics(pre_calculated_stats=aggregated_stats)

        # 4. Combine the results
        all_metrics = {**aggregated_stats, **complex_metrics}

        # Map results to the PerformanceStats Pydantic schema
        stats = PerformanceStats(**all_metrics)
        return PerformanceMetrics(stats=stats)

    async def get_calendar_data(
        self, trading_account_id: UUID, start_date: date, end_date: date, user_timezone: str
    ) -> List[CalendarDayData]:
        """
        Returns data aggregated by day for the calendar view, calculated efficiently in the database.
        """
        # La logica è stata spostata nel repository per efficienza.
        # Il parametro user_timezone non è più necessario qui, ma lo manteniamo per compatibilità con l'API.
        aggregated_data = await self.trade_repo.get_calendar_data_aggregated(
            trading_account_id, start_date, end_date
        )

        return [CalendarDayData(**item) for item in aggregated_data]

    async def get_processed_stats(
        self, trading_account_id: UUID, start_date: date, end_date: date
    ) -> ProcessedStats:
        """
        Returns aggregated stats, calculated efficiently in the database using a single optimized query.
        """
        from decimal import Decimal

        # Unica chiamata al repository per ottenere tutti i dati pre-aggregati
        aggregated_data = await self.trade_repo.get_processed_stats_aggregated(
            trading_account_id, start_date, end_date
        )

        raw_by_strategy = aggregated_data["by_strategy"]
        raw_by_day_of_week = aggregated_data["by_day_of_week"]
        raw_daily_pnl = aggregated_data["daily_pnl"]

        # 1. Process stats by strategy
        by_strategy = {
            item['strategy_name']: StrategyPerformance(
                trade_count=item['trade_count'],
                total_pnl=item['total_pnl'],
                win_rate=(item['winning_trades'] / item['trade_count'] * 100) if item['trade_count'] > 0 else 0,
            )
            for item in raw_by_strategy
        }
        max_abs_pnl = max((abs(s.total_pnl) for s in by_strategy.values()), default=Decimal('0.0'))

        # 2. Process stats by day of the week
        day_map = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"}
        by_day_of_week = {day: {"total_pnl": Decimal('0.0'), "trade_count": 0} for day in day_map.values()}
        for item in raw_by_day_of_week:
            day_name = day_map.get(item['day_of_week'])
            if day_name:
                by_day_of_week[day_name] = {
                    "total_pnl": item['total_pnl'],
                    "trade_count": item['trade_count'],
                }

        # 3. Process daily PnL to get win/loss days and monthly/weekly totals
        winning_days = 0
        losing_days = 0
        breakeven_days = 0
        monthly_totals = {}
        weekly_totals = {}

        for item in raw_daily_pnl:
            pnl = item['daily_pnl']
            trade_date = item['trade_date']

            if pnl > 0: winning_days += 1
            elif pnl < 0: losing_days += 1
            else: breakeven_days += 1

            month_key = trade_date.strftime("%Y-%m")
            monthly_totals[month_key] = monthly_totals.get(month_key, Decimal('0.0')) + pnl

            iso_year, iso_week, _ = trade_date.isocalendar()
            week_key = f"{iso_year}-W{iso_week:02d}"
            if week_key not in weekly_totals:
                weekly_totals[week_key] = {"total_pnl": Decimal('0.0'), "trading_days": set()}
            weekly_totals[week_key]["total_pnl"] += pnl
            weekly_totals[week_key]["trading_days"].add(trade_date)

        # Finalize weekly totals by counting unique days
        for week_key in weekly_totals:
            weekly_totals[week_key]["trading_days"] = len(weekly_totals[week_key]["trading_days"])

        return ProcessedStats(
            by_strategy=by_strategy,
            max_abs_pnl_by_strategy=max_abs_pnl,
            by_day_of_week=by_day_of_week,
            win_loss_days=WinLossDays(winningDays=winning_days, losingDays=losing_days, breakEvenDays=breakeven_days),
            monthly_totals=monthly_totals,
            weekly_totals=weekly_totals
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
        Returns data for the equity curve chart, calculated efficiently in the database.
        """
        trading_account = await self.trading_account_repo.get_by_id(trading_account_id)
        initial_balance = trading_account.initial_balance if trading_account else 0.0

        # La query del repo calcola il P&L cumulativo per ogni trade
        aggregated_points = await self.trade_repo.get_equity_curve_aggregated(
            trading_account_id, start_date, end_date
        )

        # Aggiungiamo il bilancio iniziale a ogni punto per ottenere il valore assoluto della curva
        # Convertiamo i datetime in oggetti date per la validazione Pydantic
        labels = [start_date] + [point['label'].date() for point in aggregated_points]
        data = [float(initial_balance)] + [float(float(initial_balance) + float(point['value'])) for point in aggregated_points]

        return EquityCurveData(labels=labels, data=data)

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

        # Get the equity curve for the day by reusing the existing service method
        equity_curve = await self.get_equity_curve(trading_account_id, day, day)

        # Get the list of trades for the day
        trades_for_day = [TradeRead.model_validate(trade) for trade in calculator.trades]

        return DailySummary(
            stats=stats,
            cumulative_pnl_series=equity_curve,
            trades=trades_for_day
        )

    async def get_tag_performance_stats(
        self, trading_account_id: UUID, start_date: date, end_date: date
    ) -> List[TagPerformanceStat]:
        """
        Calculates and returns performance statistics for each tag.
        """
        raw_stats = await self.trade_repo.get_tag_performance_stats(
            trading_account_id=trading_account_id,
            start_date=start_date,
            end_date=end_date,
        )
        return [TagPerformanceStat.model_validate(row) for row in raw_stats]