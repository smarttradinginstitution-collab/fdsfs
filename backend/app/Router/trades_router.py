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

from app.Schemas.trade import TradeRead, TradeCreate, TradeUpdate
from app.Schemas.analytics import (
    PerformanceMetrics,
    CalendarDayData,
    ProcessedStats,
    VantageScoreData,
    EquityCurveData,
    TradeSummary,
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


@router.delete("/{trade_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trade(
    trade_id: UUID,
    claims: dict = Depends(get_current_claims),
    service: TradeService = Depends(),
):
    return await controller.delete_trade(claims, trade_id, service)
