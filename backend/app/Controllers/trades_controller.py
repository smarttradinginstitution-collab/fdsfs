# app/Controllers/trades_controller.py
from __future__ import annotations

from typing import List, Optional
from uuid import UUID
from datetime import date

from fastapi import HTTPException, status

from app.Services.trade_service import TradeService
from app.Services.analytics_service import AnalyticsService
from app.Schemas.trade import TradeRead, TradeCreate, TradeUpdate
from app.Schemas.tag import TagRead
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


class TradesController:
    """
    Controller puro: nessun APIRouter qui.
    Riceve parametri dal router e delega ai Services.
    Gestisce qui le HTTPException per tenere il router super snello.
    """

    # --- Endpoints di Analisi ---
    async def get_performance_metrics(
        self,
        trading_account_id: UUID,
        start_date: date,
        end_date: date,
        service: AnalyticsService,
    ) -> PerformanceMetrics:
        return await service.get_performance_metrics(trading_account_id, start_date, end_date)

    async def get_calendar_data(
        self,
        trading_account_id: UUID,
        start_date: date,
        end_date: date,
        user_timezone: str,
        service: AnalyticsService,
    ) -> List[CalendarDayData]:
        return await service.get_calendar_data(trading_account_id, start_date, end_date, user_timezone)

    async def get_processed_stats(
        self,
        trading_account_id: UUID,
        start_date: date,
        end_date: date,
        service: AnalyticsService,
    ) -> ProcessedStats:
        return await service.get_processed_stats(trading_account_id, start_date, end_date)

    async def get_vantage_score(
        self,
        trading_account_id: UUID,
        start_date: date,
        end_date: date,
        service: AnalyticsService,
    ) -> VantageScoreData:
        return await service.get_vantage_score(trading_account_id, start_date, end_date)

    async def get_equity_curve(
        self,
        trading_account_id: UUID,
        start_date: date,
        end_date: date,
        service: AnalyticsService,
    ) -> EquityCurveData:
        return await service.get_equity_curve(trading_account_id, start_date, end_date)

    async def get_trade_summary(
        self,
        trading_account_id: UUID,
        start_date: date,
        end_date: date,
        service: AnalyticsService,
    ) -> TradeSummary:
        return await service.get_trade_summary(trading_account_id, start_date, end_date)

    async def get_financial_summary(
        self,
        claims: dict,
        trade_id: UUID,
        service: TradeService,
    ) -> TradeFinancialSummary:
        """
        Handles the request for a trade's financial summary.
        Delegates to the service and handles exceptions.
        """
        summary = await service.get_financial_summary(claims, trade_id)
        # The service layer handles the 404 for the trade itself.
        return summary

    async def get_daily_summary(
        self,
        trading_account_id: UUID,
        day: date,
        service: AnalyticsService,
    ) -> DailySummary:
        """
        Handles the request for a full daily summary.
        Delegates to the analytics service.
        """
        return await service.get_daily_summary(trading_account_id, day)

    # --- CRUD Trades ---
    async def create_trade(
        self,
        claims: dict,
        trade_data: TradeCreate,
        service: TradeService,
    ) -> TradeRead:
        return await service.create_trade(claims, trade_data)

    async def list_trades_for_trading_account(
        self,
        claims: dict,
        trading_account_id: UUID,
        start_date: Optional[date],
        end_date: Optional[date],
        service: TradeService,
    ) -> list[TradeRead]:
        return await service.list_trades_by_trading_account(
            claims=claims,
            trading_account_id=trading_account_id,
            start_date=start_date,
            end_date=end_date,
        )

    async def list_recent_trades(
        self,
        claims: dict,
        service: TradeService,
    ) -> List[TradeRead]:
        """Lists the 20 most recent trades for the current user."""
        return await service.get_recent_trades(claims=claims)

    async def get_trade(
        self,
        claims: dict,
        trade_id: UUID,
        service: TradeService,
    ) -> TradeRead:
        trade = await service.get_trade(claims, trade_id)
        if not trade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trade non trovato o non appartenente all'utente.",
            )
        return trade

    async def update_trade(
        self,
        claims: dict,
        trade_id: UUID,
        trade_data: TradeUpdate,
        service: TradeService,
    ) -> TradeRead:
        updated_trade = await service.update_trade(claims, trade_id, trade_data)
        if not updated_trade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trade non trovato o non appartenente all'utente.",
            )
        return updated_trade

    async def delete_trade(
        self,
        claims: dict,
        trade_id: UUID,
        service: TradeService,
    ) -> None:
        success = await service.delete_trade(claims, trade_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trade non trovato o non appartenente all'utente.",
            )
        return None

    # --- Trade <> Tag Association ---
    async def get_trade_tags(
        self,
        claims: dict,
        trade_id: UUID,
        service: TradeService,
    ) -> List[TagRead]:
        """
        Handles the request for getting all tags associated with a trade.
        """
        return await service.get_trade_tags(claims, trade_id)

    async def update_trade_tags(
        self,
        claims: dict,
        trade_id: UUID,
        tag_ids: List[UUID],
        service: TradeService,
    ) -> List[TagRead]:
        """
        Handles the request for updating the tags associated with a trade.
        """
        return await service.update_trade_tags(claims, trade_id, tag_ids)

    async def update_trade_labels(
        self,
        claims: dict,
        trade_id: UUID,
        label_ids: List[UUID],
        label_type: str,
        service: TradeService,
    ) -> List[TagRead]:
        """
        Handles the request for updating various labels (mistakes, psychology, etc.) associated with a trade.
        """
        return await service.update_trade_labels(claims, trade_id, label_ids, label_type)
