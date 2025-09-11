from pydantic import BaseModel

class VantageScoreData(BaseModel):
    """Schema for the Vantage Score data response."""
    vantage_score: float
    profit_factor_score: float
    avg_win_loss_score: float
    max_drawdown_score: float
    win_rate_score: float
    consistency_score: float
    recovery_factor_score: float

    class Config:
        from_attributes = True
