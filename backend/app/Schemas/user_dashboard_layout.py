from __future__ import annotations
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class UserDashboardLayoutBase(BaseModel):
    """
    Base schema for user dashboard layout.
    The layout is a list of grid items, where each item has position, size, and an identifier.
    """
    layout: List[Dict[str, Any]] = Field(..., description="The list of widgets and their layout properties.", example=[
        {"x": 0, "y": 0, "w": 2, "h": 2, "i": "0"},
        {"x": 2, "y": 0, "w": 2, "h": 4, "i": "1"},
    ])

class UserDashboardLayoutCreate(UserDashboardLayoutBase):
    """
    Schema for creating a new dashboard layout for a user.
    """
    user_id: UUID

class UserDashboardLayoutUpdate(UserDashboardLayoutBase):
    """
    Schema for updating an existing dashboard layout.
    """
    pass

class UserDashboardLayoutRead(UserDashboardLayoutBase):
    """
    Schema for reading a dashboard layout, including database-generated fields.
    `id`, `created_at`, and `updated_at` are optional to allow for returning
    a default, non-persisted layout for new users.
    """
    id: Optional[int] = None
    user_id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
