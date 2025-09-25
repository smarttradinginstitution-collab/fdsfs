from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import date

from .trade import TradeRead # Import for TradeSummary

# --- Schema for Performance Metrics Endpoint ---

class PerformanceMetrics(BaseModel):
    """Schema for the aggregated performance metrics response."""
    trade_count: int = 0
    total_pl: float = 0.0
    winning_trades_count: int = 0
    losing_trades_count: int = 0
    breakeven_trades_count: int = 0
    win_rate: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    profit_factor: Optional[float] = None
    expectancy: float = 0.0
    largest_profit: float = 0.0
    largest_loss: float = 0.0
    avg_trade_pnl: float = 0.0
    max_consecutive_wins: int = 0
    max_consecutive_losses: int = 0
    avg_realized_rr: float = 0.0
    max_drawdown_abs: float = 0.0
    sharpe_ratio: float = 0.0
    average_hold_time: float = 0.0 # in minutes

    class Config:
        from_attributes = True

# --- Schema for Calendar Data Endpoint ---

class CalendarData(BaseModel):
    """Schema for daily data used in the calendar heatmap."""
    date: date
    pnl: float
    trade_count: int
    winning_trades_count: int

    class Config:
        from_attributes = True

# --- Schema for Equity Curve Endpoint ---

class EquityCurveData(BaseModel):
    """Schema for the equity curve data response."""
    labels: List[str] = Field(..., description="Labels for the X-axis (e.g., dates)")
    data: List[float] = Field(..., description="Cumulative P&L values for the Y-axis")

    class Config:
        from_attributes = True


# --- Schema for Trade Summary Endpoint ---

class TradeSummary(BaseModel):
    """Schema for the trade summary response, combining stats and trades."""
    stats: PerformanceMetrics = Field(..., description="Performance metrics for the period")
    trades: List[TradeRead] = Field(..., description="List of trades within the period")
    cumulative_pnl_series: EquityCurveData = Field(..., description="Equity curve for the period")

    class Config:
        from_attributes = True


# --- Schemas for the more detailed Processed Stats Endpoint ---

class AggregatedStats(BaseModel):
    """Aggregated stats for a specific group (e.g., by strategy or day)."""
    total_pnl: float
    trade_count: int
    winning_trades: int
    win_rate: float

class WinLossDaysStats(BaseModel):
    """Statistics on winning/losing days."""
    winning_days: int
    losing_days: int
    breakeven_days: int

class WeeklySummaryStats(BaseModel):
    """Summary statistics for a week."""
    total_pnl: float
    trading_days: int

class ProcessedStats(BaseModel):
    """
    A comprehensive schema for detailed, pre-processed statistics,
    often used for more complex dashboard widgets.
    """
    general_stats: PerformanceMetrics = Field(..., description="Overall performance metrics")
    daily_data: Dict[str, AggregatedStats] = Field(default_factory=dict, description="Data aggregated by day (key: YYYY-MM-DD)")
    by_strategy: Dict[str, AggregatedStats] = Field(default_factory=dict, description="Data aggregated by strategy")
    max_abs_pnl_by_strategy: float = Field(0.0, description="Max absolute P&L by strategy for chart normalization")
    by_day_of_week: Dict[str, AggregatedStats] = Field(default_factory=dict, description="Data aggregated by day of the week")
    win_loss_days: WinLossDaysStats
    monthly_totals: Dict[str, float] = Field(default_factory=dict, description="Data aggregated by month (key: YYYY-MM)")
    weekly_totals: Dict[str, WeeklySummaryStats] = Field(default_factory=dict, description="Data aggregated by ISO week (key: YYYY-Www)")

    class Config:
        from_attributes = True