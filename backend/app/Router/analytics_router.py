from __future__ import annotations
from typing import List
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends

from app.Controllers.analytics_controller import AnalyticsController
from app.Schemas.analytics import TagPerformanceStat
from app.Router.auth import get_current_claims

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
    dependencies=[Depends(get_current_claims)],
)

controller = AnalyticsController()

from app.Services.analytics_service import AnalyticsService
from app.Schemas.analytics_query import AnalyticsQuery

@router.post("/tags-performance", response_model=List[TagPerformanceStat])
async def get_tags_performance(
    query: AnalyticsQuery,
    start_date: date,
    end_date: date,
    service: AnalyticsService = Depends(),
):
    return await controller.get_tags_performance_stats(
        trading_account_ids=query.trading_account_ids,
        start_date=start_date,
        end_date=end_date,
        service=service,
    )