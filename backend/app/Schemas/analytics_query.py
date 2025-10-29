# backend/app/Schemas/analytics.py
from __future__ import annotations

from typing import List, Optional
from uuid import UUID
from datetime import date
from pydantic import BaseModel, Field

class AnalyticsQuery(BaseModel):
    trading_account_ids: List[UUID]
