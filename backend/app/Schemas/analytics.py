# app/Schemas/analytics.py
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import date

# --- Schemi per /performance/metrics ---
class PerformanceStats(BaseModel):
    net_pnl: float = 0.0
    roi_percentage: float = 0.0
    gross_profit: float = 0.0
    gross_loss: float = 0.0
    win_rate: float = 0.0
    trade_count: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    breakeven_trades: int = 0
    profit_factor: Optional[float] = None
    profit_factor_label: str = "N/A"
    avg_win: float = 0.0
    avg_loss: float = 0.0
    expectancy: float = 0.0
    average_trade_pnl: float = 0.0
    largest_profit: float = 0.0
    largest_loss: float = 0.0
    max_consecutive_wins: int = 0
    max_consecutive_losses: int = 0
    max_drawdown_abs: float = 0.0
    max_drawdown_percentage: float = 0.0
    sharpe_ratio: float = 0.0
    average_hold_time: float = 0.0 # in minuti
    avg_realized_rr: float = 0.0

class PerformanceMetrics(BaseModel):
    stats: PerformanceStats

# --- Schemi per /calendar/data ---
class CalendarDayData(BaseModel):
    date: date
    pnl: float
    trade_count: int
    winning_trades_count: int

# --- Schemi per /vantage-score ---
class VantageScoreData(BaseModel):
    vantage_score: int
    win_rate_score: int
    profit_factor_score: int
    avg_win_loss_score: int
    recovery_factor_score: int
    max_drawdown_score: int
    consistency_score: int

# --- Schemi per /equity-curve ---
class EquityCurveData(BaseModel):
    labels: List[date]
    data: List[float]

class TradeSummary(BaseModel):
    stats: PerformanceStats
    cumulative_pnl_series: EquityCurveData

# --- Schemi per /processed-stats ---
class StrategyPerformance(BaseModel):
    trade_count: int
    total_pnl: float
    win_rate: float

class DayOfWeekPerformance(BaseModel):
    total_pnl: float
    trade_count: int

class WinLossDays(BaseModel):
    winningDays: int
    losingDays: int
    breakEvenDays: int

class ProcessedStats(BaseModel):
    by_strategy: Dict[str, StrategyPerformance]
    max_abs_pnl_by_strategy: float
    by_day_of_week: Dict[str, DayOfWeekPerformance]
    win_loss_days: WinLossDays
    monthly_totals: Dict[str, float]
    weekly_totals: Dict[str, Dict[str, Any]]

# --- Schemi per /trades/kpi-dashboard ---

class CumulativePnlPoint(BaseModel):
    """Rappresenta un singolo punto dati nel grafico P&L cumulativo."""
    trade_order: int
    cumulative_pnl: float

class NetCumulativePnlData(BaseModel):
    """Contiene i dati per la card Net Cumulative P&L."""
    total: float
    series: List[CumulativePnlPoint]

class KpiDashboardData(BaseModel):
    """Schema per i dati del KPI Dashboard nella pagina Trades."""
    net_cumulative_pnl: NetCumulativePnlData = Field(..., alias="netCumulativePnl")
    profit_factor: Optional[float] = Field(..., alias="profitFactor")
    win_percentage: float = Field(..., alias="winPercentage")
    winning_trades: int = Field(..., alias="winningTrades")
    losing_trades: int = Field(..., alias="losingTrades")
    avg_win: float = Field(..., alias="avgWin")
    avg_loss: float = Field(..., alias="avgLoss")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "netCumulativePnl": {
                    "total": 1374183.95,
                    "series": [
                        { "trade_order": 1, "cumulative_pnl": 500.50 },
                        { "trade_order": 2, "cumulative_pnl": 1200.75 },
                    ]
                },
                "profitFactor": 5.68,
                "winPercentage": 66.67,
                "avgWin": 13023.90,
                "avgLoss": -4584.78
            }
        }