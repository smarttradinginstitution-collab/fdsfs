# backend/app/Schemas/stats.py
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from .trade import TradeRead

# --- Schemas for Processed Stats Endpoint ---

class GeneralStats(BaseModel):
    """Statistiche generali sul periodo filtrato."""
    total_pnl: float = Field(..., description="Profitto e perdita totali")
    trade_count: int = Field(..., description="Numero totale di trade")
    winning_trades: int = Field(..., description="Numero di trade in profitto")
    losing_trades: int = Field(..., description="Numero di trade in perdita")
    breakeven_trades: int = Field(..., description="Numero di trade a zero")
    gross_profit: float = Field(..., description="Profitto lordo totale (somma dei P&L positivi)")
    gross_loss: float = Field(..., description="Perdita lorda totale (somma dei valori assoluti dei P&L negativi)")
    total_risk: float = Field(..., description="Rischio totale cumulato (se disponibile)")

class AggregatedStats(BaseModel):
    """Statistiche aggregate per un gruppo specifico (es. per strategia o giorno)."""
    total_pnl: float = Field(..., description="Profitto e perdita totali per questo gruppo")
    trade_count: int = Field(..., description="Numero di trade per questo gruppo")
    winning_trades: int = Field(..., description="Numero di trade in profitto per questo gruppo")
    win_rate: float = Field(..., description="Percentuale di trade vincenti (0-100)")

class WinLossDaysStats(BaseModel):
    """Statistiche sui giorni di trading."""
    winning_days: int = Field(..., description="Numero di giorni con P&L > 0")
    losing_days: int = Field(..., description="Numero di giorni con P&L < 0")
    breakeven_days: int = Field(..., description="Numero di giorni con P&L = 0")

class WeeklySummaryStats(BaseModel):
    """Statistiche di riepilogo per una settimana."""
    total_pnl: float = Field(..., description="P&L totale della settimana")
    trading_days: int = Field(..., description="Numero di giorni con almeno un trade nella settimana")

class ProcessedStats(BaseModel):
    """Schema di risposta per l'endpoint delle statistiche processate."""
    general_stats: GeneralStats = Field(..., description="Statistiche generali")
    daily_data: Dict[str, AggregatedStats] = Field(default_factory=dict, description="Dati aggregati per giorno (chiave: YYYY-MM-DD)")
    by_strategy: Dict[str, AggregatedStats] = Field(default_factory=dict, description="Dati aggregati per strategia")
    max_abs_pnl_by_strategy: float = Field(0.0, description="Il massimo P&L in valore assoluto tra tutte le strategie, per la normalizzazione dei grafici.")
    by_day_of_week: Dict[str, AggregatedStats] = Field(default_factory=dict, description="Dati aggregati per giorno della settimana (es. 'Lunedì')")
    win_loss_days: WinLossDaysStats = Field(..., description="Conteggio dei giorni di profitto/perdita")
    monthly_totals: Dict[str, float] = Field(default_factory=dict, description="Dati aggregati per mese (chiave: YYYY-MM)")
    weekly_totals: Dict[str, WeeklySummaryStats] = Field(default_factory=dict, description="Dati aggregati per settimana ISO (chiave: YYYY-Www)")

# --- Schema for Equity Curve Endpoint ---

class EquityCurveData(BaseModel):
    """Schema di risposta per l'endpoint della equity curve."""
    labels: List[str] = Field(..., description="Etichette per l'asse X del grafico (es. date o ID trade)")
    data: List[float] = Field(..., description="Valori del P&L cumulativo per l'asse Y")


# --- Schemas for Trade Summary Endpoint ---

class SummaryStats(BaseModel):
    """Statistiche essenziali per un riepilogo di periodo."""
    net_pnl: float = Field(..., description="Profitto e perdita netti del periodo")
    trade_count: int = Field(..., description="Numero di trade nel periodo")
    winning_trades: int = Field(..., description="Numero di trade in profitto")
    losing_trades: int = Field(..., description="Numero di trade in perdita")
    breakeven_trades: int = Field(..., description="Numero di trade a zero")
    gross_profit: float = Field(..., description="Profitto lordo totale")
    gross_loss: float = Field(..., description="Perdita lorda totale")
    # ↓↓↓ cambi essenziali ↓↓↓
    profit_factor: Optional[float] = Field(
        None, description="Valore numerico del Profit Factor (può essere nullo)"
    )
    profit_factor_label: str = Field(
        "N/A", description="Etichetta testuale per il Profit Factor (es. '2.61' o '∞')"
    )
    win_rate: float = Field(
        0.0, description="Percentuale di trade vincenti (0-100)"
    )
class TradeSummary(BaseModel):
    """Schema di risposta per l'endpoint di riepilogo di un periodo specifico."""
    stats: SummaryStats
    cumulative_pnl_series: EquityCurveData


# --- Schema for Performance Metrics Endpoint ---

class PerformanceStats(BaseModel):
    """Schema for the 'stats' object in the performance metrics response."""
    total_pl: float = 0.0
    trade_count: int = 0
    winning_trades_count: int = 0
    losing_trades_count: int = 0
    breakeven_trades_count: int = 0
    win_rate: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    expectancy: float = 0.0
    average_trade_pnl: float = 0.0
    largest_profit: float = 0.0
    largest_loss: float = 0.0
    max_consecutive_wins: int = 0
    max_consecutive_losses: int = 0
    avg_realized_rr: float = 0.0
    max_drawdown_abs: float = 0.0
    max_drawdown_percent: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0
    recovery_factor: Optional[float] = 0.0 # Can be inf
    average_hold_time: float = 0.0
    profit_factor_label: str = "N/A"
    var_95: float = 0.0
    cvar_95: float = 0.0
    total_pnl_longs: float = 0.0
    total_pnl_shorts: float = 0.0
    longs_count: int = 0
    shorts_count: int = 0
    sell_efficiency: float = 0.0
    total_efficiency: float = 0.0
    planned_rr: float = 0.0
    skewness: float = 0.0
    kurtosis: float = 0.0


class ChartData(BaseModel):
    labels: List[str]
    data: List[float]

class RMultipleData(BaseModel):
    labels: List[str]
    data: List[int]

class SetupChartData(BaseModel):
    setup: str
    total_pl: float

class PerformanceMetricsResponse(BaseModel):
    """Schema di risposta per l'endpoint delle performance metrics."""
    stats: PerformanceStats
    trades: List[TradeRead]
    equity_curve_data: ChartData
    setup_chart_data: List[SetupChartData]
    r_multiple_data: RMultipleData
    performance_by_day: ChartData
    performance_by_hour: ChartData
