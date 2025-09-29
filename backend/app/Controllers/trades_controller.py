# app/Controllers/trades_controller.py
from __future__ import annotations

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.Services.trade_service import TradeService
from app.Services.analytics_service import AnalyticsService
from app.Schemas.trade import TradeRead, TradeCreate, TradeUpdate
from app.Schemas.analytics import (
    PerformanceMetrics,
    CalendarDayData,
    ProcessedStats,
    VantageScoreData,
    EquityCurveData,
    TradeSummary
)
from app.Router.auth import get_current_claims
from datetime import date

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
    setups: Optional[List[str]] = Query(None),
    service: AnalyticsService = Depends(),
):
    return await service.get_performance_metrics(trading_account_id, start_date, end_date, setups)

@router.get("/calendar/data/{trading_account_id}", response_model=List[CalendarDayData])
async def get_calendar_data(
    trading_account_id: UUID,
    start_date: date,
    end_date: date,
    user_timezone: str,
    setups: Optional[List[str]] = Query(None),
    service: AnalyticsService = Depends(),
):
    return await service.get_calendar_data(trading_account_id, start_date, end_date, user_timezone, setups)

@router.get("/processed-stats/{trading_account_id}", response_model=ProcessedStats)
async def get_processed_stats(
    trading_account_id: UUID,
    start_date: date,
    end_date: date,
    setups: Optional[List[str]] = Query(None),
    service: AnalyticsService = Depends(),
):
    return await service.get_processed_stats(trading_account_id, start_date, end_date, setups)

@router.get("/vantage-score/{trading_account_id}", response_model=VantageScoreData)
async def get_vantage_score(
    trading_account_id: UUID,
    start_date: date,
    end_date: date,
    setups: Optional[List[str]] = Query(None),
    service: AnalyticsService = Depends(),
):
    return await service.get_vantage_score(trading_account_id, start_date, end_date, setups)

@router.get("/equity-curve/{trading_account_id}", response_model=EquityCurveData)
async def get_equity_curve(
    trading_account_id: UUID,
    start_date: date,
    end_date: date,
    setups: Optional[List[str]] = Query(None),
    service: AnalyticsService = Depends(),
):
    return await service.get_equity_curve(trading_account_id, start_date, end_date, setups)

@router.get("/summary/{trading_account_id}", response_model=TradeSummary)
async def get_trade_summary(
    trading_account_id: UUID,
    start_date: date,
    end_date: date,
    setups: Optional[List[str]] = Query(None),
    service: AnalyticsService = Depends(),
):
    return await service.get_trade_summary(trading_account_id, start_date, end_date, setups)


@router.post("/", response_model=TradeRead, status_code=status.HTTP_201_CREATED)
async def create_trade(
    trade_data: TradeCreate,
    claims: dict = Depends(get_current_claims),
    service: TradeService = Depends(),
):
    """
    Crea un nuovo Trade.
    Il `trading_account_id` nel body determina a quale account appartiene.
    Il servizio verificherà che l'utente sia il proprietario del trading account.
    """
    return await service.create_trade(claims, trade_data)


@router.get("/by-trading-account/{trading_account_id}", response_model=List[TradeRead])
async def get_trades_for_trading_account(
    trading_account_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    claims: dict = Depends(get_current_claims),
    service: TradeService = Depends(),
):
    """
    Recupera i trades per un specifico Trading Account, con filtro opzionale per data.
    """
    return await service.list_trades_by_trading_account(
        claims=claims,
        trading_account_id=trading_account_id,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/{trade_id}", response_model=TradeRead)
async def get_trade(
    trade_id: UUID,
    claims: dict = Depends(get_current_claims),
    service: TradeService = Depends(),
):
    """
    Recupera un singolo Trade per ID.
    """
    trade = await service.get_trade(claims, trade_id)
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade non trovato o non appartenente all'utente.",
        )
    return trade


@router.put("/{trade_id}", response_model=TradeRead)
async def update_trade(
    trade_id: UUID,
    trade_data: TradeUpdate,
    claims: dict = Depends(get_current_claims),
    service: TradeService = Depends(),
):
    """
    Aggiorna un Trade esistente.
    """
    updated_trade = await service.update_trade(claims, trade_id, trade_data)
    if not updated_trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade non trovato o non appartenente all'utente.",
        )
    return updated_trade


@router.delete("/{trade_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trade(
    trade_id: UUID,
    claims: dict = Depends(get_current_claims),
    service: TradeService = Depends(),
):
    """
    Elimina un Trade.
    """
    success = await service.delete_trade(claims, trade_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade non trovato o non appartenente all'utente.",
        )
    return None