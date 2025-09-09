# backend/app/Schemas/stats.py
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List, Dict

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

class WinLossDaysStats(BaseModel):
    """Statistiche sui giorni di trading."""
    winning_days: int = Field(..., description="Numero di giorni con P&L > 0")
    losing_days: int = Field(..., description="Numero di giorni con P&L < 0")
    breakeven_days: int = Field(..., description="Numero di giorni con P&L = 0")

class ProcessedStats(BaseModel):
    """Schema di risposta per l'endpoint delle statistiche processate."""
    general_stats: GeneralStats = Field(..., description="Statistiche generali")
    daily_data: Dict[str, AggregatedStats] = Field(..., description="Dati aggregati per giorno (chiave: YYYY-MM-DD)")
    by_strategy: Dict[str, AggregatedStats] = Field(..., description="Dati aggregati per strategia")
    by_day_of_week: Dict[str, AggregatedStats] = Field(..., description="Dati aggregati per giorno della settimana (es. 'Lunedì')")
    win_loss_days: WinLossDaysStats = Field(..., description="Conteggio dei giorni di profitto/perdita")

# --- Schema for Equity Curve Endpoint ---

class EquityCurveData(BaseModel):
    """Schema di risposta per l'endpoint della equity curve."""
    labels: List[str] = Field(..., description="Etichette per l'asse X del grafico (es. date o ID trade)")
    data: List[float] = Field(..., description="Valori del P&L cumulativo per l'asse Y")
