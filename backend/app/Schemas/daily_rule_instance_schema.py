from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
import datetime

class DailyRuleInstanceBase(BaseModel):
    status: str

class DailyRuleInstanceCreate(DailyRuleInstanceBase):
    manual_rule_id: UUID
    trading_account_id: UUID
    daily_journal_id: UUID
    date: datetime.date

class DailyRuleInstanceUpdate(BaseModel):
    status: Optional[str] = None

class DailyRuleInstanceSchema(DailyRuleInstanceBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    manual_rule_id: UUID
    trading_account_id: UUID
    daily_journal_id: UUID
    date: datetime.date
    name: Optional[str] = None # This will be populated from the related rule

    # This is a bit of a hack to get the name from the related rule
    # A better solution might be a custom resolver
    def __init__(self, **data):
        # The 'rule_template' relationship is loaded in the repository
        if 'rule_template' in data and hasattr(data['rule_template'], 'name'):
            data['name'] = data['rule_template'].name
        super().__init__(**data)
