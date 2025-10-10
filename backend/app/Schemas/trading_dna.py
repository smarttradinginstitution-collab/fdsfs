from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Literal, Any, Dict
from uuid import UUID

from app.Schemas.analytics import EquityCurveData

# --- Reusable Sub-schemas ---

class LabelItem(BaseModel):
    id: UUID
    name: str
    color: str | None = None

class ComboElement(BaseModel):
    type: Literal["Tag", "Mistake", "PsychologyState", "NewsImpact"]
    group: str | None = None  # Only for Tags
    item: LabelItem

class Combo(BaseModel):
    elements: List[ComboElement]

class ComboMetrics(BaseModel):
    trade_count: int
    win_rate_percent: float
    average_r_multiple: float
    total_pnl: float

# --- Main Report Component Schemas ---

class AnalyzedCombo(BaseModel):
    combo: Combo
    metrics: ComboMetrics

class GroupInfo(BaseModel):
    id: UUID
    name: str

class GroupPerformance(BaseModel):
    group: GroupInfo
    metrics: ComboMetrics

class ComparativeEquityCurve(BaseModel):
    filtered_series: EquityCurveData
    baseline_series: EquityCurveData

# --- Top-Level Report Schema ---

class TradingDnaReport(BaseModel):
    golden_combos: List[AnalyzedCombo]
    toxic_combos: List[AnalyzedCombo]