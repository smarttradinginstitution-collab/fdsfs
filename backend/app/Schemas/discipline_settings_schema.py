from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from uuid import UUID
import datetime

class DisciplineSettingsBase(BaseModel):
    trading_days: Optional[List[int]] = None
    start_day_by: Optional[datetime.time] = None
    link_trades_to_playbook_threshold: Optional[int] = None
    trade_has_stop_loss_threshold: Optional[int] = None
    max_loss_per_trade_type: Optional[str] = None
    max_loss_per_trade_value: Optional[float] = None
    max_loss_per_day: Optional[float] = None

class DisciplineSettingsCreate(DisciplineSettingsBase):
    pass

class DisciplineSettingsUpdate(DisciplineSettingsBase):
    pass

class DisciplineSettingsSchema(DisciplineSettingsBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    general_account_id: UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime