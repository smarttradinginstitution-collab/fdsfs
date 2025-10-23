# backend/app/Controllers/soa_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from datetime import date

from app.Services.analytics_service import AnalyticsService
from app.Schemas.soa import SOAOverallAnalysis
from app.Router.dependencies import get_current_general_account_id

router = APIRouter()

@router.get(
    "/analytics/{trading_account_id}/soa",
    response_model=SOAOverallAnalysis,
    tags=["Analytics"],
    summary="Get Strength & Opportunity Analysis (SOA)",
)
async def get_soa_analysis(
    trading_account_id: UUID,
    start_date: date,
    end_date: date,
    analytics_service: AnalyticsService = Depends(),
    general_account_id: UUID = Depends(get_current_general_account_id),
) -> SOAOverallAnalysis:
    """
    Retrieves the complete Strength & Opportunity Analysis (SOA) for a user.

    This endpoint orchestrates a complex, multi-level analysis of trade data
    between a start and end date, including clustering, causal analysis, and
    parametric optimization. It returns both the numerical results and
    structured, human-readable advice.

    Args:
        trading_account_id (UUID): The ID of the trading account to analyze.
        start_date (date): The start date of the analysis period.
        end_date (date): The end date of the analysis period.
        analytics_service (AnalyticsService): Injected dependency for the
            analytics service.
        general_account_id (UUID): The general account ID of the current user,
            injected for authorization.

    Returns:
        SOAOverallAnalysis: A Pydantic model containing the full, structured
        results of the analysis.

    Raises:
        HTTPException: 404 if no data is available for the period or if the
        user is not authorized to access the trading account.
    """
    soa_results = await analytics_service.get_soa_analysis(
        trading_account_id=trading_account_id,
        start_date=start_date,
        end_date=end_date,
        general_account_id=general_account_id,
    )
    if not soa_results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No data available for the selected period or user unauthorized.",
        )
    return soa_results
