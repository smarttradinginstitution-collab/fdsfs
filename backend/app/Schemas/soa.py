# backend/app/Schemas/soa.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class SOASL_TPOptimizationSchema(BaseModel):
    sl_optimal_p90: Optional[float] = Field(None, description="Livello ottimale di Stop Loss (90° percentile dello stress ratio)")
    sl_optimal_p95: Optional[float] = Field(None, description="Livello ottimale di Stop Loss (95° percentile dello stress ratio)")
    tp_optimal_median: Optional[float] = Field(None, description="Livello ottimale di Take Profit (mediana del potential R)")
    tp_optimal_mean: Optional[float] = Field(None, description="Livello ottimale di Take Profit (media del potential R)")
    avg_user_stress_ratio: Optional[float] = Field(None, description="Stress ratio medio utilizzato dall'utente")
    avg_user_planned_tp_r: Optional[float] = Field(None, description="TP medio in R pianificato dall'utente")


class SOADurationExpectancySchema(BaseModel):
    decile: int
    avg_duration: float
    expectancy: float
    win_rate: float
    avg_win_pnl: float
    avg_loss_pnl: float
    trade_count: int

class SOACausalAnalysisItemSchema(BaseModel):
    attribute_id: Any = Field(..., alias='attribute_col') # Mantiene il nome originale per flessibilità
    cluster_label: str
    trade_count: int
    total_pnl: float
    probability: float # P(Cluster | Attributo)
    sn_mean: float = Field(..., alias='SN_mean')
    ep_mean: float = Field(..., alias='EP_mean')
    rrv_mean: float = Field(..., alias='RRv_mean')
    es_mean: float = Field(..., alias='ES_mean')
    rer_mean: float = Field(..., alias='RER_mean')
    dd_mean: float = Field(..., alias='DD_mean')

    class Config:
        populate_by_name = True

class SOACausalAnalysisSchema(BaseModel):
    playbook: List[SOACausalAnalysisItemSchema]
    tag: List[SOACausalAnalysisItemSchema]
    mistake: List[SOACausalAnalysisItemSchema]
    psychology: List[SOACausalAnalysisItemSchema]
    news: List[SOACausalAnalysisItemSchema]
    rule: List[SOACausalAnalysisItemSchema]

class SOAClusterSummarySchema(BaseModel):
    trade_count: int
    sn: float = Field(..., alias='SN')
    ep: float = Field(..., alias='EP')
    rrv: float = Field(..., alias='RRv')
    es: float = Field(..., alias='ES')
    rer: float = Field(..., alias='RER')
    dd: float = Field(..., alias='DD')
    p_l: float
    realized_r_multiple: float
    duration_minutes: float

    class Config:
        populate_by_name = True

class SOADrawdownZScoreSchema(BaseModel):
    z_score: float
    current_drawdown_usd: float
    average_drawdown_usd: float
    stddev_drawdown_usd: float

class SOAOverallAnalysis(BaseModel):
    clusters_summary: Dict[str, SOAClusterSummarySchema]
    causal_analysis: SOACausalAnalysisSchema
    parametric_optimization: Dict[str, Any] # Semplificato per ora
    predictive_metrics: Dict[str, Any]
    drawdown_z_score: SOADrawdownZScoreSchema
    trade_details: List[Dict[str, Any]]
    headline_insight: Optional[str] = None
