# app/Schemas/playbook.py
from __future__ import annotations
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

# La classe RulesGroupRead verrà importata in seguito.
# Pydantic e FastAPI gestiscono i forward reference (stringhe)
# in modo da non dover importare subito.


# Schema di base con i campi comuni
class PlaybookBase(BaseModel):
    title: Optional[str] = Field(None, description="The title of the playbook")
    description: Optional[str] = Field(None, description="The description of the playbook")
    private: Optional[bool] = Field(None, description="Whether the playbook is private")
    color: Optional[str] = Field(None, description="The color associated with the playbook")
    icon_name: Optional[str] = Field(None, description="The name of the icon associated with the playbook")

    model_config = {"from_attributes": True}

# Schema per la creazione di un playbook (usato nel body delle richieste POST)
class PlaybookCreate(PlaybookBase):
    title: str = Field(..., description="The title of the playbook is required for creation")
    description: str = Field(..., description="The description of the playbook is required")
    private: bool = Field(False, description="Whether the playbook is private. Defaults to False")


# Schema per l'aggiornamento di un playbook (usato nel body delle richieste PUT/PATCH)
class PlaybookUpdate(PlaybookBase):
    pass # title, description e private sono già opzionali in PlaybookBase

# Schema per le statistiche calcolate di un playbook
class PlaybookStats(BaseModel):
    total_trades: int = 0
    win_rate: float = 0.0
    profit_factor: Optional[float] = None
    expectancy: float = 0.0
    avg_winner: float = 0.0
    avg_loser: float = 0.0
    net_pnl: float = 0.0

# Schema per la lettura di un playbook (usato nelle risposte GET)
class PlaybookRead(PlaybookBase):
    id: UUID
    general_account_id: UUID
    created_at: datetime
    description: str
    private: bool
    rules_groups: List["RulesGroupRead"] = []
    stats: Optional[PlaybookStats] = None


class PlaybookAdminRead(BaseModel):
    general_account_id: UUID
    user_email: str
    playbooks: List[PlaybookRead]

    model_config = {"from_attributes": True}


# Alla fine, quando tutti i modelli sono definiti, si può fare:
# PlaybookRead.model_rebuild()
# Ma con FastAPI, questo viene gestito automaticamente.


# --- Schemi per la pagina di dettaglio del Playbook ---

from app.Schemas.analytics import EquityCurveData

class PlaybookAnalyticsMetrics(BaseModel):
    net_pnl: float = Field(0.0, description="Net Profit and Loss")
    trades: int = Field(0, description="Total number of trades")
    win_rate: float = Field(0.0, description="Win rate percentage")
    profit_factor: Optional[float] = Field(None, description="Profit factor")
    missed_trades: int = Field(0, description="Number of missed trades")
    expectancy: float = Field(0.0, description="Expectancy per trade")
    rules_followed: float = Field(0.0, description="Percentage of rules followed")
    average_winner: float = Field(0.0, description="Average winning trade")
    average_loser: float = Field(0.0, description="Average losing trade")
    largest_profit: float = Field(0.0, description="Largest single profit")
    largest_loss: float = Field(0.0, description="Largest single loss")
    total_r_multiple: float = Field(0.0, description="Sum of all R-multiples")

class PlaybookAnalytics(BaseModel):
    id: UUID
    title: str
    metrics: PlaybookAnalyticsMetrics
    equity_curve: EquityCurveData

    model_config = {"from_attributes": True}