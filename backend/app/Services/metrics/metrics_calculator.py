# app/Services/metrics/metrics_calculator.py
from __future__ import annotations

from typing import List, Dict, Optional, Any
import numpy as np
from datetime import date, datetime
from decimal import Decimal

from app.Models.trade import Trade
from app.Models.rule_playbook import RulePlaybook

class MetricsCalculator:
    """
    Centralizes all performance metrics calculations for a trading account.
    All calculations are based on the provided trades and initial balance.
    """

    def __init__(self, trades: List[Trade], initial_balance: float):
        self.trades = sorted(
            trades,
            key=lambda t: t.exit_timestamp or t.entry_timestamp or datetime.min
        )
        self.initial_balance = Decimal(initial_balance) if initial_balance is not None else Decimal('0.0')
        self.pnl_series = [Decimal(str(t.p_l)) for t in self.trades if t.p_l is not None]
        self.trade_count = len(self.pnl_series)

        # Pre-calculate basic stats to avoid redundant calculations
        self._calculate_basic_stats()

    def _calculate_basic_stats(self):
        """Pre-calculates basic statistics used by multiple methods."""
        if self.trade_count == 0:
            self.net_pnl = Decimal('0.0')
            self.winning_trades_list = []
            self.losing_trades_list = []
            self.winning_trades_count = 0
            self.losing_trades_count = 0
            self.breakeven_trades_count = 0
            self.gross_profit = Decimal('0.0')
            self.gross_loss = Decimal('0.0')
            return

        self.net_pnl = sum(self.pnl_series)
        self.winning_trades_list = [t for t in self.trades if t.p_l is not None and t.p_l > 0]
        self.losing_trades_list = [t for t in self.trades if t.p_l is not None and t.p_l < 0]

        self.winning_trades_count = len(self.winning_trades_list)
        self.losing_trades_count = len(self.losing_trades_list)

        total_classified = self.winning_trades_count + self.losing_trades_count
        self.breakeven_trades_count = len(self.trades) - total_classified

        self.gross_profit = sum(Decimal(str(t.p_l)) for t in self.winning_trades_list)
        self.gross_loss = abs(sum(Decimal(str(t.p_l)) for t in self.losing_trades_list))

    def get_all_metrics(self, pre_calculated_stats: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Returns a dictionary containing all calculated performance metrics.
        Accepts an optional dictionary of pre-calculated stats to avoid redundant calculations.
        """
        if self.trade_count == 0 and not pre_calculated_stats:
            return self._get_default_metrics()

        base_metrics = {}
        # If pre_calculated_stats are provided, use them. Otherwise, calculate them.
        if pre_calculated_stats:
            base_metrics = pre_calculated_stats
            net_pnl = Decimal(str(base_metrics.get("net_pnl", 0.0)))
            gross_profit = Decimal(str(base_metrics.get("gross_profit", 0.0)))
            gross_loss = Decimal(str(base_metrics.get("gross_loss", 0.0)))
            winning_trades_count = base_metrics.get("winning_trades", 0)
            losing_trades_count = base_metrics.get("losing_trades", 0)
            trade_count = base_metrics.get("trade_count", 0)
            avg_win = Decimal(str(base_metrics.get("avg_win", 0.0)))
            avg_loss = Decimal(str(base_metrics.get("avg_loss", 0.0)))
        else:
            # Fallback to in-memory calculation if no pre-calculated stats are provided
            net_pnl = self.net_pnl
            gross_profit = self.gross_profit
            gross_loss = self.gross_loss
            winning_trades_count = self.winning_trades_count
            losing_trades_count = self.losing_trades_count
            trade_count = self.trade_count
            avg_win = gross_profit / winning_trades_count if winning_trades_count > 0 else Decimal('0')
            avg_loss = gross_loss / losing_trades_count if losing_trades_count > 0 else Decimal('0')
            base_metrics = {
                "net_pnl": net_pnl,
                "gross_profit": gross_profit,
                "gross_loss": gross_loss,
                "winning_trades": winning_trades_count,
                "losing_trades": losing_trades_count,
                "breakeven_trades": self.breakeven_trades_count,
                "trade_count": trade_count,
                "avg_win": avg_win,
                "avg_loss": avg_loss,
                "largest_profit": max(self.pnl_series) if any(p > 0 for p in self.pnl_series) else 0,
                "largest_loss": min(self.pnl_series) if any(p < 0 for p in self.pnl_series) else 0,
                "avg_realized_rr": self._calculate_avg_realized_rr(),
            }

        win_rate = (winning_trades_count / trade_count) * 100 if trade_count > 0 else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else None

        # These metrics still require the full trade list for now
        # Equity curve data is now generated by a dedicated method
        equity_curve_data = self.get_equity_curve()
        max_drawdown_abs, max_drawdown_perc = self.calculate_max_drawdown(equity_curve_data["data"])

        # Consolidate all metrics into a single dictionary
        complex_metrics = {
            "roi_percentage": self.calculate_roi(net_pnl),
            "win_rate": win_rate, # Recalculate for consistency, it's fast
            "profit_factor": profit_factor,
            "profit_factor_label": f"{profit_factor:.2f}" if profit_factor is not None else "∞",
            "expectancy": self._calculate_expectancy(win_rate, avg_win, avg_loss),
            "average_trade_pnl": net_pnl / trade_count if trade_count > 0 else 0,
            "max_drawdown_abs": max_drawdown_abs,
            "max_drawdown_percentage": max_drawdown_perc,
            "sharpe_ratio": self._calculate_sharpe_ratio(),
            # These still require iterating the list
            "max_consecutive_wins": self._calculate_max_consecutive_wins_losses()[0],
            "max_consecutive_losses": self._calculate_max_consecutive_wins_losses()[1],
            "average_hold_time": self._calculate_average_hold_time(),
        }
        return {**base_metrics, **complex_metrics}

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

    def get_equity_curve(self) -> Dict[str, List[Any]]:
        """
        Generates the data required for plotting an equity curve.
        Returns labels as date objects to comply with Pydantic schema.
        """
        if self.trade_count == 0:
            # Return initial balance but no labels, as there are no trades/dates
            return {"labels": [], "data": [float(self.initial_balance)]}

        # Use exit timestamps (as date objects) for the labels of the equity curve
        labels = [
            (t.exit_timestamp or t.entry_timestamp).date()
            for t in self.trades
        ]

        # Calculate the cumulative P/L over time
        cumulative_pnl = np.cumsum(self.pnl_series)

        # Create the equity curve data points, starting with the initial balance
        equity_curve_data = [float(self.initial_balance)] + [
            float(self.initial_balance) + float(pnl) for pnl in cumulative_pnl
        ]

        # The data list has one more item (initial balance) than the labels list.
        # The frontend will need to handle this, e.g., by adding an "Initial" label
        # or by aligning the data points to the labels. For API correctness, we
        # return only the dates corresponding to trades.

        return {"labels": labels, "data": equity_curve_data}

    def calculate_roi(self, net_pnl: Optional[Decimal] = None) -> float:
        """Calculates the Return on Investment (ROI) based on initial balance."""
        if self.initial_balance == 0:
            return 0.0

        # Use provided net_pnl if available, otherwise use the one calculated in the instance
        pnl_to_use = net_pnl if net_pnl is not None else self.net_pnl

        return (pnl_to_use / self.initial_balance) * 100

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

    def _calculate_expectancy(self, win_rate, avg_win, avg_loss) -> Decimal:
        """Calculates the expectancy."""
        win_rate_dec = Decimal(win_rate) / Decimal(100)
        loss_rate = Decimal(self.losing_trades_count / self.trade_count) if self.trade_count > 0 else Decimal(0)
        return (win_rate_dec * avg_win) - (loss_rate * avg_loss)

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

    @staticmethod
    def calculate_for_rule(rule: RulePlaybook, total_playbook_trades: int) -> Dict[str, Any]:
        """
        Calculates performance metrics for a single rule based on the trades that followed it.
        """
        trades_followed = rule.trades
        num_trades_followed = len(trades_followed)

        # Calculate Follow Rate
        # This is calculated first as it's independent of P/L
        follow_rate = (num_trades_followed / total_playbook_trades) * 100 if total_playbook_trades > 0 else 0.0

        if num_trades_followed == 0:
            return {
                "follow_rate": follow_rate,
                "net_pnl": 0.0,
                "profit_factor": None,
                "win_rate": 0.0
            }

        # Calculate Net P/L
        net_pnl = sum(Decimal(str(trade.p_l)) for trade in trades_followed if trade.p_l is not None)

        # Calculate Win Rate
        winning_trades = [t for t in trades_followed if t.p_l is not None and t.p_l > 0]
        win_rate = (len(winning_trades) / num_trades_followed) * 100 if num_trades_followed > 0 else 0.0

        # Calculate Profit Factor
        gross_profit = sum(Decimal(str(t.p_l)) for t in winning_trades)
        losing_trades = [t for t in trades_followed if t.p_l is not None and t.p_l < 0]
        gross_loss = abs(sum(Decimal(str(t.p_l)) for t in losing_trades))

        profit_factor = gross_profit / gross_loss if gross_loss > 0 else None

        return {
            "follow_rate": follow_rate,
            "net_pnl": net_pnl,
            "profit_factor": profit_factor,
            "win_rate": win_rate
        }