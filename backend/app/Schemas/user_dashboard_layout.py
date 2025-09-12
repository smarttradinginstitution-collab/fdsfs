from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from typing import List

# Schema for an individual grid item in the layout
class LayoutItemSchema(BaseModel):
    i: str
    x: int
    y: int
    w: int
    h: int

# The layout is an array of these items
LayoutConfigSchema = List[LayoutItemSchema]

# Base schema for layout data
class UserDashboardLayoutBase(BaseModel):
    layout_config: LayoutConfigSchema

# Schema for creating a new layout
class UserDashboardLayoutCreate(UserDashboardLayoutBase):
    pass

# Schema for updating an existing layout
class UserDashboardLayoutUpdate(UserDashboardLayoutBase):
    pass

# Schema for reading layout data from the database
class UserDashboardLayoutRead(UserDashboardLayoutBase):
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
