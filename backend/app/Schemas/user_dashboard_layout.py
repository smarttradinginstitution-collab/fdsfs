# app/Schemas/user_dashboard_layout.py

from __future__ import annotations

from typing import Any, Dict, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

from pydantic import Field

class WidgetItem(BaseModel):
    i: str
    x: int | None = None
    y: int | None = None
    w: int | None = None
    h: int | None = None
    component: str | None = None
    isDraggable: bool | None = Field(default=None)
    isResizable: bool | None = Field(default=None)
    static: bool | None = Field(default=None)

class ZonedLayout(BaseModel):
    stats: List[WidgetItem]
    main: List[WidgetItem]
    charts: List[WidgetItem]

class UserDashboardLayoutUpdate(BaseModel):
    """Schema for updating a user's dashboard layout."""
    layout: ZonedLayout


class UserDashboardLayoutCreate(BaseModel):
    """Schema for creating a user's dashboard layout."""
    user_id: UUID
    layout: ZonedLayout


class UserDashboardLayoutRead(BaseModel):
    """Schema for reading a user's dashboard layout."""
    id: UUID
    user_id: UUID
    layout: ZonedLayout
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
