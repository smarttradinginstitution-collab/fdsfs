# backend/app/Schemas/soa.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from uuid import UUID

class SOASL_TPOptimizationSchema(BaseModel):
    """Data model for Stop Loss and Take Profit optimization results."""
    sl_optimal_p90: Optional[float] = Field(None, description="Optimal Stop Loss level based on the 90th percentile of stress ratio on winning trades.")
    sl_optimal_p95: Optional[float] = Field(None, description="Optimal Stop Loss level based on the 95th percentile of stress ratio on winning trades.")
    tp_optimal_median: Optional[float] = Field(None, description="Optimal Take Profit level based on the median potential R of winning trades.")
    tp_optimal_mean: Optional[float] = Field(None, description="Optimal Take Profit level based on the mean potential R of winning trades.")
    avg_user_stress_ratio: Optional[float] = Field(None, description="The user's average stress ratio, used as a proxy for their typical Stop Loss.")
    avg_user_planned_tp_r: Optional[float] = Field(None, description="The user's average planned Take Profit in R-multiples.")

class SOADurationExpectancySchema(BaseModel):
    """Data model for trade expectancy calculated across duration deciles."""
    decile: int = Field(..., description="The duration decile group (0-9).")
    avg_duration: float = Field(..., description="The average trade duration in this decile (minutes).")
    expectancy: float = Field(..., description="The calculated expectancy for this decile.")
    win_rate: float = Field(..., description="The win rate for trades in this decile.")
    avg_win_pnl: float = Field(..., description="The average P/L of winning trades in this decile.")
    avg_loss_pnl: float = Field(..., description="The average P/L of losing trades in this decile.")
    trade_count: int = Field(..., description="The number of trades in this decile.")

class SOACausalAnalysisItemSchema(BaseModel):
    """Represents the analysis of a single attribute's performance within a cluster."""
    attribute_id: Any = Field(..., alias='attribute_col', description="The ID of the attribute being analyzed (e.g., playbook_id, tag_id).")
    cluster_label: str = Field(..., description="The label of the cluster (e.g., 'A', 'B').")
    trade_count: int = Field(..., description="Number of trades for this attribute in this cluster.")
    total_pnl: float = Field(..., description="Total P/L for this attribute in this cluster.")
    probability: float = Field(..., description="Probability of a trade with this attribute falling into this cluster, P(Cluster | Attribute).")
    sn_mean: float = Field(..., alias='SN_mean', description="Mean Normalized Stress (SN) for this group.")
    ep_mean: float = Field(..., alias='EP_mean', description="Mean Profit Efficiency (EP) for this group.")
    rrv_mean: float = Field(..., alias='RRv_mean', description="Mean Reversal Ratio (RRv) for this group.")
    es_mean: float = Field(..., alias='ES_mean', description="Mean Stop Efficiency (ES) for this group.")
    rer_mean: float = Field(..., alias='RER_mean', description="Mean R:R Execution Ratio (RER) for this group.")
    dd_mean: float = Field(..., alias='DD_mean', description="Mean Duration Deviation (DD) for this group.")

    class Config:
        populate_by_name = True

class SOACausalAnalysisSchema(BaseModel):
    """Container for causal analysis results across different attribute types."""
    playbook: List[SOACausalAnalysisItemSchema]
    tag: List[SOACausalAnalysisItemSchema]
    mistake: List[SOACausalAnalysisItemSchema]
    psychology: List[SOACausalAnalysisItemSchema]
    news: List[SOACausalAnalysisItemSchema]
    rule: List[SOACausalAnalysisItemSchema]

class SOAClusterSummarySchema(BaseModel):
    """Represents the average characteristics of a single trade cluster."""
    trade_count: int = Field(..., description="Total number of trades in this cluster.")
    sn: float = Field(..., alias='SN', description="Mean Normalized Stress (SN) of the cluster.")
    ep: float = Field(..., alias='EP', description="Mean Profit Efficiency (EP) of the cluster.")
    rrv: float = Field(..., alias='RRv', description="Mean Reversal Ratio (RRv) of the cluster.")
    es: float = Field(..., alias='ES', description="Mean Stop Efficiency (ES) of the cluster.")
    rer: float = Field(..., alias='RER', description="Mean R:R Execution Ratio (RER) of the cluster.")
    dd: float = Field(..., alias='DD',
    description="Mean Duration Deviation (DD) of the cluster.")
    p_l: float = Field(..., description="Mean P/L of the cluster.")
    realized_r_multiple: float = Field(..., description="Mean realized R-multiple of the cluster.")
    duration_minutes: float = Field(..., description="Mean trade duration in minutes for the cluster.")

    class Config:
        populate_by_name = True

class SOADrawdownZScoreSchema(BaseModel):
    """Data model for the drawdown Z-score analysis."""
    z_score: float = Field(..., description="The Z-score of the current drawdown, indicating its statistical significance.")
    current_drawdown_usd: float = Field(..., description="The current drawdown value in USD.")
    average_drawdown_usd: float = Field(..., description="The historical average drawdown in USD.")
    stddev_drawdown_usd: float = Field(..., description="The historical standard deviation of drawdowns in USD.")

class StructuredAdvice(BaseModel):
    """Container for all human-readable, actionable advice."""
    sl_advice: Optional[str] = Field(None, description="Textual advice regarding Stop Loss optimization.")
    tp_advice: Optional[str] = Field(None, description="Textual advice regarding Take Profit optimization.")
    psychological_advice: Optional[str] = Field(None, description="Textual advice regarding psychological patterns (autocorrelation, drawdown).")

class SOAOverallAnalysis(BaseModel):
    """The main response model for the complete Strength & Opportunity Analysis."""
    clusters_summary: Dict[str, SOAClusterSummarySchema] = Field(..., description="Summary of average characteristics for each identified trade cluster.")
    causal_analysis: SOACausalAnalysisSchema = Field(..., description="Analysis of how different attributes (playbooks, tags, etc.) correlate with clusters.")
    parametric_optimization: Dict[str, Any] = Field(..., description="Results of SL/TP optimization and duration-based expectancy analysis.")
    predictive_metrics: Dict[str, Any] = Field(..., description="Metrics with potential predictive value, like R-multiple autocorrelation.")
    drawdown_z_score: SOADrawdownZScoreSchema = Field(..., description="Analysis of the current drawdown's statistical significance.")
    trade_details: List[Dict[str, Any]] = Field(..., description="A list of all individual trades included in the analysis with their calculated metrics.")
    structured_advice: StructuredAdvice = Field(..., description="A container for all generated human-readable, actionable advice.")
    headline_insight: Optional[str] = Field(None, description="A single, high-level actionable insight generated from the most critical metric.")
    error: Optional[str] = Field(None, description="An optional error message if part of the analysis failed.")
