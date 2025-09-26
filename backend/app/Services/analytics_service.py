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

        # --- Basic Calcs ---
        pnl_list = [t.p_l for t in trades if t.p_l is not None]
        trade_count = len(pnl_list)
        if trade_count == 0:
            return PerformanceMetrics(stats=PerformanceStats())

        net_pnl = sum(pnl_list)

        winning_trades_list = [t for t in trades if t.p_l is not None and t.p_l > 0]
        losing_trades_list = [t for t in trades if t.p_l is not None and t.p_l < 0]

        winning_trades_count = len(winning_trades_list)
        losing_trades_count = len(losing_trades_list)

        win_rate = (winning_trades_count / trade_count) * 100

        gross_profit = sum(t.p_l for t in winning_trades_list)
        gross_loss = abs(sum(t.p_l for t in losing_trades_list))

        avg_win = gross_profit / winning_trades_count if winning_trades_count > 0 else 0
        avg_loss = gross_loss / losing_trades_count if losing_trades_count > 0 else 0

        profit_factor = gross_profit / gross_loss if gross_loss > 0 else None
        profit_factor_label = f"{profit_factor:.2f}" if profit_factor is not None else "∞"

        # --- Advanced Metrics ---

        # Sort trades for time-series calculations
        sorted_trades = sorted(trades, key=lambda t: t.exit_timestamp or t.entry_timestamp)
        pnl_series = [t.p_l for t in sorted_trades if t.p_l is not None]

        # Max Consecutive Wins/Losses
        max_consecutive_wins = 0
        max_consecutive_losses = 0
        current_wins = 0
        current_losses = 0
        for pnl in pnl_series:
            if pnl > 0:
                current_wins += 1
                current_losses = 0
            elif pnl < 0:
                current_losses += 1
                current_wins = 0
            max_consecutive_wins = max(max_consecutive_wins, current_wins)
            max_consecutive_losses = max(max_consecutive_losses, current_losses)

        # Average Hold Time
        total_hold_time = 0
        trades_with_duration = 0
        for trade in trades:
            if trade.entry_timestamp and trade.exit_timestamp:
                hold_time = (trade.exit_timestamp - trade.entry_timestamp).total_seconds()
                total_hold_time += hold_time
                trades_with_duration += 1

        average_hold_time = (total_hold_time / trades_with_duration) / 60 if trades_with_duration > 0 else 0 # in minutes

        # Expectancy
        loss_rate = (losing_trades_count / trade_count) if trade_count > 0 else 0
        expectancy = ((win_rate / 100) * avg_win) - (loss_rate * avg_loss)

        # Max Drawdown
        cumulative_pnl = np.cumsum(pnl_series)
        peak = np.maximum.accumulate(cumulative_pnl)
        drawdown = peak - cumulative_pnl
        max_drawdown_abs = np.max(drawdown) if len(drawdown) > 0 else 0

        # Sharpe Ratio (assuming risk-free rate is 0)
        pnl_std_dev = np.std(pnl_list) if len(pnl_list) > 1 else 0
        average_trade_pnl = net_pnl / trade_count
        sharpe_ratio = (average_trade_pnl / pnl_std_dev) if pnl_std_dev > 0 else 0

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
            largest_profit=max(pnl_list) if any(p > 0 for p in pnl_list) else 0,
            largest_loss=min(pnl_list) if any(p < 0 for p in pnl_list) else 0,
            max_consecutive_wins=max_consecutive_wins,
            max_consecutive_losses=max_consecutive_losses,
            average_hold_time=average_hold_time,
            expectancy=expectancy,
            average_trade_pnl=average_trade_pnl,
            max_drawdown_abs=float(max_drawdown_abs),
            sharpe_ratio=sharpe_ratio
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
        trades = await self.trade_repo.get_filtered_trades(trading_account_id, start_date, end_date)

        weekly_totals = {}
        if trades:
            for trade in trades:
                if trade.entry_timestamp:
                    trade_date = trade.entry_timestamp.date()
                    iso_year, iso_week, _ = trade_date.isocalendar()
                    week_key = f"{iso_year}-W{iso_week:02d}"

                    if week_key not in weekly_totals:
                        weekly_totals[week_key] = {"total_pnl": 0.0, "trading_days": set()}

                    weekly_totals[week_key]["total_pnl"] += trade.p_l or 0
                    weekly_totals[week_key]["trading_days"].add(trade_date)

        # Converti i set di giorni in conteggi
        for week_key, data in weekly_totals.items():
            weekly_totals[week_key]["trading_days"] = len(data["trading_days"])

        # --- Inizializzazione delle strutture dati ---
        by_strategy: Dict[str, Dict[str, Any]] = {}
        by_day_of_week: Dict[str, Dict[str, float]] = {
            day: {"total_pnl": 0.0, "trade_count": 0}
            for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        }
        daily_pnl: Dict[date, float] = {}
        monthly_totals: Dict[str, float] = {}

        if trades:
            for trade in trades:
                if not trade.entry_timestamp or trade.p_l is None:
                    continue

                trade_date = trade.entry_timestamp.date()

                # --- By Strategy (Playbook) ---
                if trade.playbooks:
                    for playbook in trade.playbooks:
                        if playbook.title not in by_strategy:
                            by_strategy[playbook.title] = {"trade_count": 0, "total_pnl": 0.0, "winning_trades": 0}

                        by_strategy[playbook.title]["trade_count"] += 1
                        by_strategy[playbook.title]["total_pnl"] += trade.p_l
                        if trade.p_l > 0:
                            by_strategy[playbook.title]["winning_trades"] += 1

                # --- By Day of Week ---
                day_name = trade_date.strftime("%A")
                by_day_of_week[day_name]["total_pnl"] += trade.p_l
                by_day_of_week[day_name]["trade_count"] += 1

                # --- Daily and Monthly PnL ---
                if trade_date not in daily_pnl:
                    daily_pnl[trade_date] = 0.0
                daily_pnl[trade_date] += trade.p_l

                month_key = trade_date.strftime("%Y-%m")
                if month_key not in monthly_totals:
                    monthly_totals[month_key] = 0.0
                monthly_totals[month_key] += trade.p_l

        # --- Final Calcs ---

        # Win/Loss/Breakeven Days
        winning_days = sum(1 for pnl in daily_pnl.values() if pnl > 0)
        losing_days = sum(1 for pnl in daily_pnl.values() if pnl < 0)
        breakeven_days = sum(1 for pnl in daily_pnl.values() if pnl == 0)
        win_loss_days = WinLossDays(winningDays=winning_days, losingDays=losing_days, breakEvenDays=breakeven_days)

        # Finalize By Strategy data
        processed_by_strategy = {
            name: StrategyPerformance(
                trade_count=data["trade_count"],
                total_pnl=data["total_pnl"],
                win_rate=(data["winning_trades"] / data["trade_count"]) * 100 if data["trade_count"] > 0 else 0
            ) for name, data in by_strategy.items()
        }

        # Max Abs PnL for scaling charts
        max_abs_pnl_by_strategy = max(abs(s.total_pnl) for s in processed_by_strategy.values()) if processed_by_strategy else 0

        return ProcessedStats(
            by_strategy=processed_by_strategy,
            max_abs_pnl_by_strategy=max_abs_pnl_by_strategy,
            by_day_of_week=by_day_of_week,
            win_loss_days=win_loss_days,
            monthly_totals=monthly_totals,
            weekly_totals=weekly_totals
        )

    async def get_vantage_score(
        self,
        trading_account_id: UUID,
        start_date: date,
        end_date: date
    ) -> VantageScoreData:
        metrics_data = await self.get_performance_metrics(trading_account_id, start_date, end_date)
        stats = metrics_data.stats

        if stats.trade_count < 5:  # Non calcolare se ci sono troppo pochi trade
            return VantageScoreData(
                vantage_score=0, win_rate_score=0, profit_factor_score=0,
                avg_win_loss_score=0, recovery_factor_score=0,
                max_drawdown_score=0, consistency_score=0
            )

        # --- Funzioni di Normalizzazione (Scalano un valore in un punteggio 0-100) ---
        def normalize(value, min_val, max_val, invert=False):
            """Normalizza un valore in una scala 0-100, con protezione dalla divisione per zero."""
            value = max(min_val, min(value, max_val))
            denominator = max_val - min_val
            if denominator == 0:
                return 0  # Ritorna 0 se il range è nullo per evitare errori
            score = ((value - min_val) / denominator) * 100
            return 100 - score if invert else score

        # --- Calcolo dei Sub-Scores ---

        # 1. Win Rate Score (Scala lineare 0-100%)
        win_rate_score = normalize(stats.win_rate, 0, 100)

        # 2. Profit Factor Score (Valore ottimale intorno a 2-3, capped a 5)
        profit_factor_score = normalize(stats.profit_factor or 0, 0, 5)

        # 3. Avg Win/Loss Ratio Score (Rapporto tra vincita media e perdita media)
        avg_win_loss_ratio = (stats.avg_win / stats.avg_loss) if stats.avg_loss > 0 else 5.0 # Cap a 5 se non ci sono perdite
        avg_win_loss_score = normalize(avg_win_loss_ratio, 0, 5) # Cap a 5

        # 4. Recovery Factor Score (Net PnL / Max Drawdown)
        recovery_factor = (stats.net_pnl / stats.max_drawdown_abs) if stats.max_drawdown_abs > 0 else 0
        recovery_factor_score = normalize(recovery_factor, 0, 10) # Cap a 10

        # 5. Max Drawdown Score (Invertito: meno drawdown è meglio. Normalizzato contro Net PnL)
        # Se non c'è profitto, qualsiasi drawdown è "cattivo"
        if stats.net_pnl > 0:
            drawdown_ratio = (stats.max_drawdown_abs / stats.net_pnl) * 100
            max_drawdown_score = normalize(drawdown_ratio, 0, 100, invert=True)
        else:
            max_drawdown_score = 0 # Penalità massima se il PnL è negativo

        # 6. Consistency Score (Usiamo lo Sharpe Ratio come proxy per la consistenza)
        # Lo Sharpe Ratio può essere negativo, normalizziamolo da -1 a 2.
        consistency_score = normalize(stats.sharpe_ratio, -1, 2)


        # --- Calcolo del Punteggio Finale ---
        scores = [
            win_rate_score,
            profit_factor_score,
            avg_win_loss_score,
            recovery_factor_score,
            max_drawdown_score,
            consistency_score
        ]
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