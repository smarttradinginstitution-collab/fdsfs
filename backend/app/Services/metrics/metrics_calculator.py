# app/Services/metrics/metrics_calculator.py
from __future__ import annotations

from typing import List, Dict, Optional, Any
import numpy as np
from datetime import date

from app.Models.trade import Trade

class MetricsCalculator:
    """
    Centralizes all performance metrics calculations for a trading account.
    All calculations are based on the provided trades and initial balance.
    """

    def __init__(self, trades: List[Trade], initial_balance: float):
        self.trades = sorted(trades, key=lambda t: t.exit_timestamp or t.entry_timestamp)
        self.initial_balance = initial_balance if initial_balance is not None else 0.0
        self.pnl_series = [t.p_l for t in self.trades if t.p_l is not None]
        self.trade_count = len(self.pnl_series)

        # Pre-calculate basic stats to avoid redundant calculations
        self._calculate_basic_stats()

    def _calculate_basic_stats(self):
        """Pre-calculates basic statistics used by multiple methods."""
        if self.trade_count == 0:
            self.net_pnl = 0.0
            self.winning_trades_list = []
            self.losing_trades_list = []
            self.winning_trades_count = 0
            self.losing_trades_count = 0
            self.breakeven_trades_count = 0
            self.gross_profit = 0.0
            self.gross_loss = 0.0
            return

        self.net_pnl = sum(self.pnl_series)
        self.winning_trades_list = [t for t in self.trades if t.p_l is not None and t.p_l > 0]
        self.losing_trades_list = [t for t in self.trades if t.p_l is not None and t.p_l < 0]

        self.winning_trades_count = len(self.winning_trades_list)
        self.losing_trades_count = len(self.losing_trades_list)

        total_classified = self.winning_trades_count + self.losing_trades_count
        self.breakeven_trades_count = len(self.trades) - total_classified


        self.gross_profit = sum(t.p_l for t in self.winning_trades_list)
        self.gross_loss = abs(sum(t.p_l for t in self.losing_trades_list))

    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Returns a dictionary containing all calculated performance metrics.
        This is the main method called by AnalyticsService.
        """
        if self.trade_count == 0:
            return self._get_default_metrics()

        # Core Metrics
        equity_curve_data = self.calculate_equity_curve()
        max_drawdown_abs, max_drawdown_perc = self.calculate_max_drawdown(equity_curve_data['data'])
        avg_win = self.gross_profit / self.winning_trades_count if self.winning_trades_count > 0 else 0
        avg_loss = self.gross_loss / self.losing_trades_count if self.losing_trades_count > 0 else 0
        win_rate = (self.winning_trades_count / self.trade_count) * 100 if self.trade_count > 0 else 0
        profit_factor = self.gross_profit / self.gross_loss if self.gross_loss > 0 else None

        # Processed Stats
        processed_stats = self.calculate_processed_stats()

        # Consolidate all metrics into a single dictionary
        metrics = {
            "net_pnl": self.net_pnl,
            "roi_percentage": self.calculate_roi(),
            "gross_profit": self.gross_profit,
            "gross_loss": self.gross_loss,
            "win_rate": win_rate,
            "trade_count": self.trade_count,
            "winning_trades": self.winning_trades_count,
            "losing_trades": self.losing_trades_count,
            "breakeven_trades": self.breakeven_trades_count,
            "profit_factor": profit_factor,
            "profit_factor_label": f"{profit_factor:.2f}" if profit_factor is not None else "∞",
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "largest_profit": max(self.pnl_series) if any(p > 0 for p in self.pnl_series) else 0,
            "largest_loss": min(self.pnl_series) if any(p < 0 for p in self.pnl_series) else 0,
            "max_consecutive_wins": self._calculate_max_consecutive_wins_losses()[0],
            "max_consecutive_losses": self._calculate_max_consecutive_wins_losses()[1],
            "average_hold_time": self._calculate_average_hold_time(),
            "expectancy": self._calculate_expectancy(win_rate, avg_win, avg_loss),
            "average_trade_pnl": self.net_pnl / self.trade_count if self.trade_count > 0 else 0,
            "avg_realized_rr": self._calculate_avg_realized_rr(),
            "max_drawdown_abs": max_drawdown_abs,
            "max_drawdown_percentage": max_drawdown_perc,
            "sharpe_ratio": self._calculate_sharpe_ratio(),
            "equity_curve": equity_curve_data,
            "calendar_data": self.calculate_calendar_data(),
            **processed_stats  # Unpack all processed stats into the main dictionary
        }
        return metrics

    def get_playbook_summary_metrics(self) -> Dict[str, Any]:
        """
        Calculates a summarized set of metrics, typically for a playbook.
        This is ideal for getting quick stats without all the details.
        """
        if self.trade_count == 0:
            return {
                "total_trades": 0,
                "win_rate": 0.0,
                "profit_factor": None,
                "expectancy": 0.0,
                "avg_winner": 0.0,
                "avg_loser": 0.0,
                "net_pnl": 0.0,
            }

        win_rate = (self.winning_trades_count / self.trade_count) * 100
        avg_winner = self.gross_profit / self.winning_trades_count if self.winning_trades_count > 0 else 0
        avg_loser = self.gross_loss / self.losing_trades_count if self.losing_trades_count > 0 else 0

        expectancy = self._calculate_expectancy(win_rate, avg_winner, avg_loser)

        profit_factor = self.gross_profit / self.gross_loss if self.gross_loss > 0 else None

        return {
            "total_trades": self.trade_count,
            "win_rate": win_rate,
            "profit_factor": profit_factor,
            "expectancy": expectancy,
            "avg_winner": avg_winner,
            "avg_loser": avg_loser,
            "net_pnl": self.net_pnl,
        }

    def _get_default_metrics(self) -> Dict[str, Any]:
        """Returns a dictionary with default values for when there are no trades."""
        default_processed = {
            "by_strategy": {}, "max_abs_pnl_by_strategy": 0, "by_day_of_week": {},
            "win_loss_days": {"winningDays": 0, "losingDays": 0, "breakEvenDays": 0},
            "monthly_totals": {}, "weekly_totals": {}
        }
        return {
            "net_pnl": 0.0, "roi_percentage": 0.0, "gross_profit": 0.0, "gross_loss": 0.0,
            "win_rate": 0.0, "trade_count": 0, "winning_trades": 0, "losing_trades": 0,
            "breakeven_trades": 0, "profit_factor": None, "profit_factor_label": "N/A", "avg_win": 0.0,
            "avg_loss": 0.0, "largest_profit": 0.0, "largest_loss": 0.0, "max_consecutive_wins": 0,
            "max_consecutive_losses": 0, "average_hold_time": 0.0, "expectancy": 0.0,
            "average_trade_pnl": 0.0, "avg_realized_rr": 0.0, "max_drawdown_abs": 0.0,
            "max_drawdown_percentage": 0.0, "sharpe_ratio": 0.0,
            "equity_curve": {"labels": [], "data": [self.initial_balance]},
            "calendar_data": [],
            **default_processed
        }

    def calculate_roi(self) -> float:
        """Calculates the Return on Investment (ROI) based on initial balance."""
        if self.initial_balance == 0:
            return 0.0
        return (self.net_pnl / self.initial_balance) * 100

    def calculate_equity_curve(self) -> Dict[str, List[Any]]:
        """
        Calculates the equity curve, starting from the initial balance.
        A data point is generated for each trade to show intra-day progression.
        """
        equity_data = [self.initial_balance]
        current_balance = self.initial_balance

        # The label for the initial data point is the date of the first trade, or today if no trades.
        start_date = self.trades[0].entry_timestamp.date() if self.trades else date.today()
        labels = [start_date]

        for trade in self.trades:
            if trade.p_l is not None:
                current_balance += trade.p_l
                equity_data.append(current_balance)

                # Each new data point needs a label
                trade_date = (trade.exit_timestamp or trade.entry_timestamp).date()
                labels.append(trade_date)

        return {"labels": labels, "data": equity_data}


    def calculate_max_drawdown(self, equity_curve: List[float]) -> (float, float):
        """
        Calculates the maximum drawdown from the equity curve data.
        Returns both the absolute value and the percentage.
        """
        if not equity_curve or len(equity_curve) < 2:
            return 0.0, 0.0

        peak_history = np.maximum.accumulate(equity_curve)
        drawdowns = peak_history - equity_curve

        max_drawdown_abs = np.max(drawdowns)
        if max_drawdown_abs == 0:
            return 0.0, 0.0

        # Find the peak from which the max drawdown started
        max_drawdown_index = np.argmax(drawdowns)
        peak_at_drawdown_start = peak_history[max_drawdown_index]

        if peak_at_drawdown_start == 0:
            return float(max_drawdown_abs), 0.0

        max_drawdown_perc = (max_drawdown_abs / peak_at_drawdown_start) * 100

        return float(max_drawdown_abs), float(max_drawdown_perc)

    def _calculate_max_consecutive_wins_losses(self) -> (int, int):
        """Calculates max consecutive wins and losses."""
        max_wins = 0
        max_losses = 0
        current_wins = 0
        current_losses = 0
        for pnl in self.pnl_series:
            if pnl > 0:
                current_wins += 1
                current_losses = 0
            elif pnl < 0:
                current_losses += 1
                current_wins = 0
            max_wins = max(max_wins, current_wins)
            max_losses = max(max_losses, current_losses)
        return max_wins, max_losses

    def _calculate_average_hold_time(self) -> float:
        """Calculates the average hold time in minutes."""
        total_hold_time = 0
        trades_with_duration = 0
        for trade in self.trades:
            if trade.entry_timestamp and trade.exit_timestamp:
                hold_time = (trade.exit_timestamp - trade.entry_timestamp).total_seconds()
                total_hold_time += hold_time
                trades_with_duration += 1
        return (total_hold_time / trades_with_duration) / 60 if trades_with_duration > 0 else 0

    def _calculate_expectancy(self, win_rate, avg_win, avg_loss) -> float:
        """Calculates the expectancy."""
        loss_rate = (self.losing_trades_count / self.trade_count) if self.trade_count > 0 else 0
        return ((win_rate / 100) * avg_win) - (loss_rate * avg_loss)

    def _calculate_avg_realized_rr(self) -> float:
        """Calculates the average realized R:R multiple."""
        r_multiples = [t.r_multiple for t in self.trades if t.r_multiple is not None]
        return sum(r_multiples) / len(r_multiples) if r_multiples else 0.0

    def _calculate_sharpe_ratio(self) -> float:
        """Calculates the Sharpe Ratio (assuming risk-free rate is 0)."""
        pnl_std_dev = np.std(self.pnl_series) if len(self.pnl_series) > 1 else 0
        if pnl_std_dev == 0:
            return 0.0
        average_trade_pnl = self.net_pnl / self.trade_count
        return (average_trade_pnl / pnl_std_dev) if pnl_std_dev > 0 else 0.0

    def calculate_calendar_data(self) -> List[Dict[str, Any]]:
        """Aggregates P&L and trade counts by day for the calendar view."""
        daily_summary = {}
        for trade in self.trades:
            if trade.entry_timestamp:
                trade_date = trade.entry_timestamp.date()
                if trade_date not in daily_summary:
                    daily_summary[trade_date] = {"pnl": 0, "trade_count": 0, "winning_trades_count": 0}

                daily_summary[trade_date]["pnl"] += trade.p_l or 0
                daily_summary[trade_date]["trade_count"] += 1
                if trade.p_l and trade.p_l > 0:
                    daily_summary[trade_date]["winning_trades_count"] += 1

        return [
            {
                "date": day,
                "pnl": data["pnl"],
                "trade_count": data["trade_count"],
                "winning_trades_count": data["winning_trades_count"]
            } for day, data in daily_summary.items()
        ]

    def calculate_processed_stats(self) -> Dict[str, Any]:
        """Calculates aggregated stats like 'by_strategy', 'by_day_of_week', etc."""
        if not self.trades:
            return {
                "by_strategy": {}, "max_abs_pnl_by_strategy": 0, "by_day_of_week": {},
                "win_loss_days": {"winningDays": 0, "losingDays": 0, "breakEvenDays": 0},
                "monthly_totals": {}, "weekly_totals": {}
            }

        weekly_totals = {}
        for trade in self.trades:
            if trade.entry_timestamp:
                trade_date = trade.entry_timestamp.date()
                iso_year, iso_week, _ = trade_date.isocalendar()
                week_key = f"{iso_year}-W{iso_week:02d}"
                if week_key not in weekly_totals:
                    weekly_totals[week_key] = {"total_pnl": 0.0, "trading_days": set()}
                weekly_totals[week_key]["total_pnl"] += trade.p_l or 0
                weekly_totals[week_key]["trading_days"].add(trade_date)

        for week_key, data in weekly_totals.items():
            weekly_totals[week_key]["trading_days"] = len(data["trading_days"])

        by_strategy: Dict[str, Dict[str, Any]] = {}
        by_day_of_week: Dict[str, Dict[str, float]] = {
            day: {"total_pnl": 0.0, "trade_count": 0}
            for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        }
        daily_pnl: Dict[date, float] = {}
        monthly_totals: Dict[str, float] = {}

        for trade in self.trades:
            if not trade.entry_timestamp or trade.p_l is None: continue
            trade_date = trade.entry_timestamp.date()

            if trade.playbooks:
                for playbook in trade.playbooks:
                    if playbook.title not in by_strategy:
                        by_strategy[playbook.title] = {"trade_count": 0, "total_pnl": 0.0, "winning_trades": 0}
                    by_strategy[playbook.title]["trade_count"] += 1
                    by_strategy[playbook.title]["total_pnl"] += trade.p_l
                    if trade.p_l > 0: by_strategy[playbook.title]["winning_trades"] += 1

            day_name = trade_date.strftime("%A")
            by_day_of_week[day_name]["total_pnl"] += trade.p_l
            by_day_of_week[day_name]["trade_count"] += 1

            if trade_date not in daily_pnl: daily_pnl[trade_date] = 0.0
            daily_pnl[trade_date] += trade.p_l

            month_key = trade_date.strftime("%Y-%m")
            if month_key not in monthly_totals: monthly_totals[month_key] = 0.0
            monthly_totals[month_key] += trade.p_l

        winning_days = sum(1 for pnl in daily_pnl.values() if pnl > 0)
        losing_days = sum(1 for pnl in daily_pnl.values() if pnl < 0)
        breakeven_days = sum(1 for pnl in daily_pnl.values() if pnl == 0)
        win_loss_days = {"winningDays": winning_days, "losingDays": losing_days, "breakEvenDays": breakeven_days}

        processed_by_strategy = {
            name: {
                "trade_count": data["trade_count"],
                "total_pnl": data["total_pnl"],
                "win_rate": (data["winning_trades"] / data["trade_count"]) * 100 if data["trade_count"] > 0 else 0
            } for name, data in by_strategy.items()
        }

        max_abs_pnl_by_strategy = max((abs(s['total_pnl']) for s in processed_by_strategy.values()), default=0)

        return {
            "by_strategy": processed_by_strategy,
            "max_abs_pnl_by_strategy": max_abs_pnl_by_strategy,
            "by_day_of_week": by_day_of_week,
            "win_loss_days": win_loss_days,
            "monthly_totals": monthly_totals,
            "weekly_totals": weekly_totals
        }