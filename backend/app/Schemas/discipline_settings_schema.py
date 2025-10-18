import uuid
import datetime
from pydantic import BaseModel, Field
from typing import Optional, List

class DisciplineSettingsBase(BaseModel):
    trading_days: List[int] = Field(..., description="Days of the week the checklist is active, e.g., [1,2,3,4,5]")
    start_day_by: Optional[datetime.time] = Field(None, description="The time the user should start their day by.")
    link_trades_to_playbook_threshold: Optional[int] = Field(None, ge=0, le=100, description="Percentage of trades that must be linked to a playbook.")
    trade_has_stop_loss_threshold: Optional[int] = Field(None, ge=0, le=100, description="Percentage of trades that must have a stop loss.")
    max_loss_per_trade_type: Optional[str] = Field(None, description="Type of max loss per trade: '%' or '$'")
    max_loss_per_trade_value: Optional[float] = Field(None, ge=0, description="Value for max loss per trade.")
    max_loss_per_day: Optional[float] = Field(None, ge=0, description="Maximum loss per day in dollars.")

class DisciplineSettingsUpdate(DisciplineSettingsBase):
    pass

class DisciplineSettingsRead(DisciplineSettingsBase):
    id: uuid.UUID
    general_account_id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True