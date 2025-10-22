# backend/app/Router/trades_router.py

from __future__ import annotations

from typing import List, Optional
from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, status

from app.Controllers.trades_controller import TradesController
from app.Services.trade_service import TradeService
from app.Services.analytics_service import AnalyticsService
from app.Router.auth import get_current_claims

from app.Schemas.trade import TradeRead, TradeCreate, TradeUpdate, TradeReviewUpdate
from app.Schemas.analytics import (
    PerformanceMetrics,
    CalendarDayData,
    ProcessedStats,
    VantageScoreData,
    EquityCurveData,
    TradeSummary,
    TradeFinancialSummary,
    DailySummary,
)

controller = TradesController()

router = APIRouter(
    prefix="/trades",
    tags=["Trades"],
    responses={404: {"description": "Not found"}},
)

# --- Endpoint di Analisi ---
@router.get("/performance/metrics/{trading_account_id}", response_model=PerformanceMetrics)
async def get_performance_metrics(
    trading_account_id: UUID,
    start_date: date,
    end_date: date,
    service: AnalyticsService = Depends(),
):
    return await controller.get_performance_metrics(trading_account_id, start_date, end_date, service)


@router.get("/calendar/data/{trading_account_id}", response_model=List[CalendarDayData])
async def get_calendar_data(
    trading_account_id: UUID,
    start_date: date,
    end_date: date,
    user_timezone: str,
    service: AnalyticsService = Depends(),
):
    return await controller.get_calendar_data(trading_account_id, start_date, end_date, user_timezone, service)


@router.get("/processed-stats/{trading_account_id}", response_model=ProcessedStats)
async def get_processed_stats(
    trading_account_id: UUID,
    start_date: date,
    end_date: date,
    service: AnalyticsService = Depends(),
):
    return await controller.get_processed_stats(trading_account_id, start_date, end_date, service)


@router.get("/vantage-score/{trading_account_id}", response_model=VantageScoreData)
async def get_vantage_score(
    trading_account_id: UUID,
    start_date: date,
    end_date: date,
    service: AnalyticsService = Depends(),
):
    return await controller.get_vantage_score(trading_account_id, start_date, end_date, service)


@router.get("/equity-curve/{trading_account_id}", response_model=EquityCurveData)
async def get_equity_curve(
    trading_account_id: UUID,
    start_date: date,
    end_date: date,
    service: AnalyticsService = Depends(),
):
    return await controller.get_equity_curve(trading_account_id, start_date, end_date, service)


@router.get("/summary/{trading_account_id}", response_model=TradeSummary)
async def get_trade_summary(
    trading_account_id: UUID,
    start_date: date,
    end_date: date,
    service: AnalyticsService = Depends(),
):
    return await controller.get_trade_summary(trading_account_id, start_date, end_date, service)


@router.get("/daily-summary/{trading_account_id}/{day}", response_model=DailySummary, summary="Get a full summary for a single day")
async def get_daily_summary(
    trading_account_id: UUID,
    day: date,
    service: AnalyticsService = Depends(),
):
    return await controller.get_daily_summary(trading_account_id, day, service)


@router.get("/{trade_id}/financial_summary", response_model=TradeFinancialSummary, summary="Get a financial summary for a single trade")
async def get_financial_summary(
    trade_id: UUID,
    claims: dict = Depends(get_current_claims),
    service: TradeService = Depends(),
):
    return await controller.get_financial_summary(claims, trade_id, service)


# --- CRUD Trades ---
@router.post("/", response_model=TradeRead, status_code=status.HTTP_201_CREATED)
async def create_trade(
    trade_data: TradeCreate,
    claims: dict = Depends(get_current_claims),
    service: TradeService = Depends(),
):
    return await controller.create_trade(claims, trade_data, service)


@router.get("/by-trading-account/{trading_account_id}", response_model=List[TradeRead])
async def get_trades_for_trading_account(
    trading_account_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    claims: dict = Depends(get_current_claims),
    service: TradeService = Depends(),
):
    return await controller.list_trades_for_trading_account(
        claims=claims,
        trading_account_id=trading_account_id,
        start_date=start_date,
        end_date=end_date,
        service=service,
    )


@router.get("/recent", response_model=List[TradeRead], summary="Get the last 20 trades for the current user")
async def get_recent_trades(
    claims: dict = Depends(get_current_claims),
    service: TradeService = Depends(),
):
    return await controller.list_recent_trades(claims, service)


@router.get("/{trade_id}", response_model=TradeRead)
async def get_trade(
    trade_id: UUID,
    claims: dict = Depends(get_current_claims),
    service: TradeService = Depends(),
):
    return await controller.get_trade(claims, trade_id, service)


@router.put("/{trade_id}", response_model=TradeRead)
async def update_trade(
    trade_id: UUID,
    trade_data: TradeUpdate,
    claims: dict = Depends(get_current_claims),
    service: TradeService = Depends(),
):
    return await controller.update_trade(claims, trade_id, trade_data, service)


@router.patch("/{trade_id}/review", response_model=TradeRead)
async def update_trade_review_status(
    trade_id: UUID,
    trade_data: TradeReviewUpdate,
    claims: dict = Depends(get_current_claims),
    service: TradeService = Depends(),
):
    # Poiché non esiste un controller separato, chiamiamo direttamente il service
    return await service.update_review_status(claims, trade_id, trade_data)


@router.delete("/{trade_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trade(
    trade_id: UUID,
    claims: dict = Depends(get_current_claims),
    service: TradeService = Depends(),
):
    return await controller.delete_trade(claims, trade_id, service)


# --- Trade <> Tag Association ---
from app.Schemas.tag import TagRead

@router.get("/{trade_id}/tags", response_model=List[TagRead], summary="Get all tags associated with a trade")
async def get_trade_tags(
    trade_id: UUID,
    claims: dict = Depends(get_current_claims),
    service: TradeService = Depends(),
):
    return await controller.get_trade_tags(claims, trade_id, service)


@router.post("/{trade_id}/tags", response_model=List[TagRead], summary="Update the tags associated with a trade")
async def update_trade_tags(
    trade_id: UUID,
    tag_ids: List[UUID],
    claims: dict = Depends(get_current_claims),
    service: TradeService = Depends(),
):
    return await controller.update_trade_tags(claims, trade_id, tag_ids, service)


# --- Generic Trade <> Label Association ---
from app.Schemas.mistake import MistakeRead
from app.Schemas.psychology_state import PsychologyStateRead
from app.Schemas.news_impact import NewsImpactRead
from app.Schemas.image import ImageRead
from app.Services.image_service import ImageService
from app.Router.dependencies import get_current_user, CurrentUser
from fastapi import UploadFile, File, Form

@router.post(
    "/{trade_id}/images",
    response_model=ImageRead,
    status_code=status.HTTP_201_CREATED,
    summary="Upload an image for a specific trade",
    tags=["Images"]
)
async def upload_trade_image(
    trade_id: UUID,
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    phase: Optional[str] = Form(None),
    current_user: CurrentUser = Depends(get_current_user),
    image_service: ImageService = Depends(),
):
    return await image_service.upload_trade_image(
        file=file,
        user_id=current_user.id,
        trade_id=trade_id,
        description=description,
        category=category,
        phase=phase,
    )

@router.get(
    "/{trade_id}/images",
    response_model=List[ImageRead],
    summary="Get all images associated with a trade",
    tags=["Images"]
)
async def get_trade_images(
    trade_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    image_service: ImageService = Depends(),
):
    return await image_service.get_images_for_trade(trade_id, requesting_user_id=current_user.id)


@router.post("/{trade_id}/mistakes", response_model=List[MistakeRead], summary="Update the mistakes associated with a trade")
async def update_trade_mistakes(
    trade_id: UUID,
    label_ids: List[UUID],
    claims: dict = Depends(get_current_claims),
    service: TradeService = Depends(),
):
    return await controller.update_trade_labels(claims, trade_id, label_ids, "mistakes", service)

@router.post("/{trade_id}/psychology-states", response_model=List[PsychologyStateRead], summary="Update the psychology states associated with a trade")
async def update_trade_psychology_states(
    trade_id: UUID,
    label_ids: List[UUID],
    claims: dict = Depends(get_current_claims),
    service: TradeService = Depends(),
):
    return await controller.update_trade_labels(claims, trade_id, label_ids, "psychology_states", service)

@router.post("/{trade_id}/news-impacts", response_model=List[NewsImpactRead], summary="Update the news impacts associated with a trade")
async def update_trade_news_impacts(
    trade_id: UUID,
    label_ids: List[UUID],
    claims: dict = Depends(get_current_claims),
    service: TradeService = Depends(),
):
    return await controller.update_trade_labels(claims, trade_id, label_ids, "news_impacts", service)


@router.put("/{trade_id}/rules", response_model=List[UUID], summary="Update the 'followed' rules for a trade")
async def update_trade_rules(
    trade_id: UUID,
    rule_ids: List[UUID],
    claims: dict = Depends(get_current_claims),
    service: TradeService = Depends(),
):
    """
    Updates the list of followed rules for a specific trade.
    This replaces the existing list of followed rules with the one provided.
    """
    return await controller.update_trade_rules(claims, trade_id, rule_ids, service)
