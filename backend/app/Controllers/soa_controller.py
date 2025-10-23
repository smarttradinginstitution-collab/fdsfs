# backend/app/Controllers/soa_controller.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.Infrastructure.db import get_db
from app.Services.analytics_service import AnalyticsService
from app.Schemas.soa import SOAOverallAnalysis
from app.Router.dependencies import get_current_general_account_id
import datetime
import uuid

router = APIRouter()

@router.get(
    "/{trading_account_id}/soa",
    response_model=SOAOverallAnalysis,
    summary="Get comprehensive Strength & Opportunity Analysis (SOA)",
    description="Performs a deep analysis on a collection of trades, including clustering, causal analysis, and predictive metrics."
)
async def get_soa_analysis(
    trading_account_id: uuid.UUID,
    start_date: datetime.date,
    end_date: datetime.date,
    general_account_id: uuid.UUID = Depends(get_current_general_account_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint per eseguire l'analisi SOA completa.
    """
    analytics_service = AnalyticsService(db=db)
    soa_results = await analytics_service.get_soa_analysis(
        trading_account_id=trading_account_id,
        start_date=start_date,
        end_date=end_date,
        general_account_id=general_account_id
    )
    if not soa_results:
        raise HTTPException(status_code=404, detail="No data available for the selected period or user unauthorized.")
    return soa_results
