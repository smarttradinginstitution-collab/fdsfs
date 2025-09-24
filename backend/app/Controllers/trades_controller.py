# app/Controllers/trades_controller.py
from __future__ import annotations

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from app.Services.trade_service import TradeService
from app.Schemas.trade import TradeRead, TradeCreate, TradeUpdate
from app.Router.auth import get_current_claims

router = APIRouter(
    prefix="/trades",
    tags=["Trades"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=TradeRead, status_code=status.HTTP_201_CREATED)
def create_trade(
    trade_data: TradeCreate,
    claims: dict = Depends(get_current_claims),
    service: TradeService = Depends(),
):
    """
    Crea un nuovo Trade.
    Il `trading_account_id` nel body determina a quale account appartiene.
    Il servizio verificherà che l'utente sia il proprietario del trading account.
    """
    return service.create_trade(claims, trade_data)


@router.get("/by-trading-account/{trading_account_id}", response_model=List[TradeRead])
def get_trades_for_trading_account(
    trading_account_id: UUID,
    claims: dict = Depends(get_current_claims),
    service: TradeService = Depends(),
):
    """
    Recupera tutti i trades per un specifico Trading Account.
    """
    return service.list_trades_by_trading_account(claims, trading_account_id)


@router.get("/{trade_id}", response_model=TradeRead)
def get_trade(
    trade_id: UUID,
    claims: dict = Depends(get_current_claims),
    service: TradeService = Depends(),
):
    """
    Recupera un singolo Trade per ID.
    """
    trade = service.get_trade(claims, trade_id)
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade non trovato o non appartenente all'utente.",
        )
    return trade


@router.put("/{trade_id}", response_model=TradeRead)
def update_trade(
    trade_id: UUID,
    trade_data: TradeUpdate,
    claims: dict = Depends(get_current_claims),
    service: TradeService = Depends(),
):
    """
    Aggiorna un Trade esistente.
    """
    updated_trade = service.update_trade(claims, trade_id, trade_data)
    if not updated_trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade non trovato o non appartenente all'utente.",
        )
    return updated_trade


@router.delete("/{trade_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trade(
    trade_id: UUID,
    claims: dict = Depends(get_current_claims),
    service: TradeService = Depends(),
):
    """
    Elimina un Trade.
    """
    success = service.delete_trade(claims, trade_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade non trovato o non appartenente all'utente.",
        )
    return None