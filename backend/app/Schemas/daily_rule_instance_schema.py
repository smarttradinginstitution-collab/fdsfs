from pydantic import BaseModel, ConfigDict, computed_field
from typing import Optional, TYPE_CHECKING
from uuid import UUID
import datetime

# Use TYPE_CHECKING to avoid circular imports at runtime
if TYPE_CHECKING:
    from app.Schemas.manual_rule_schema import ManualRuleRead

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

    # Define the relationship for Pydantic
    rule_template: "ManualRuleRead"

    @computed_field
    @property
    def name(self) -> str:
        """Computed field to expose the rule's name directly."""
        return self.rule_template.name

# After the class is defined, update its forward references.
# This is the standard way to handle circular dependencies with Pydantic V2.
from app.Schemas.manual_rule_schema import ManualRuleRead
DailyRuleInstanceSchema.model_rebuild()
