from __future__ import annotations
from typing import List
from uuid import UUID
from datetime import date
from fastapi import Depends

from app.Services.analytics_service import AnalyticsService
from app.Schemas.analytics import TagPerformanceStat

class AnalyticsController:
    async def get_tags_performance_stats(
        self,
        trading_account_ids: List[UUID],
        start_date: date,
        end_date: date,
        service: AnalyticsService = Depends(),
    ) -> List[TagPerformanceStat]:
        return await service.get_tag_performance_stats(
            trading_account_ids=trading_account_ids,
            start_date=start_date,
            end_date=end_date,
        )