# app/Schemas/user_dashboard_layout.py

from __future__ import annotations

from typing import Any, Dict, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class UserDashboardLayoutUpdate(BaseModel):
    """Schema for updating a user's dashboard layout."""
    layout: Dict[str, Any]


class UserDashboardLayoutRead(BaseModel):
    """Schema for reading a user's dashboard layout."""
    id: UUID
    user_id: UUID
    layout: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
