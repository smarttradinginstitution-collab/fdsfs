# backend/app/Schemas/stats.py
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List, Dict, Optional

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
    daily_data: Dict[str, AggregatedStats] = Field(..., description="Dati aggregati per giorno (chiave: YYYY-MM-DD)")
    by_strategy: Dict[str, AggregatedStats] = Field(..., description="Dati aggregati per strategia")
    max_abs_pnl_by_strategy: float = Field(0.0, description="Il massimo P&L in valore assoluto tra tutte le strategie, per la normalizzazione dei grafici.")
    by_day_of_week: Dict[str, AggregatedStats] = Field(..., description="Dati aggregati per giorno della settimana (es. 'Lunedì')")
    win_loss_days: WinLossDaysStats = Field(..., description="Conteggio dei giorni di profitto/perdita")
    monthly_totals: Dict[str, float] = Field(..., description="Dati aggregati per mese (chiave: YYYY-MM)")
    weekly_totals: Dict[str, WeeklySummaryStats] = Field(..., description="Dati aggregati per settimana ISO (chiave: YYYY-Www)")

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
    profit_factor: Optional[float] = Field(..., description="Valore numerico del Profit Factor (può essere nullo)")
    profit_factor_label: str = Field(..., description="Etichetta testuale per il Profit Factor (es. '2.61' o '∞')")
    win_rate: float = Field(..., description="Percentuale di trade vincenti (0-100)")

class TradeSummary(BaseModel):
    """Schema di risposta per l'endpoint di riepilogo di un periodo specifico."""
    stats: SummaryStats
    cumulative_pnl_series: EquityCurveData
