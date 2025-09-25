# app/Controllers/trading_account_controller.py
from __future__ import annotations

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from app.Services.trading_account_service import TradingAccountService
from app.Schemas.trading_account import TradingAccountRead, TradingAccountCreate
from app.Router.auth import get_current_claims

router = APIRouter(
    prefix="/trading-accounts",
    tags=["Trading Accounts"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=TradingAccountRead, status_code=status.HTTP_201_CREATED)
async def create_trading_account(
    account_data: TradingAccountCreate,
    claims: dict = Depends(get_current_claims),
    service: TradingAccountService = Depends(),
):
    """
    Crea un nuovo Trading Account per l'utente autenticato.
    """
    return await service.create_trading_account_for_user(claims, account_data)


@router.get("/", response_model=List[TradingAccountRead])
async def get_my_trading_accounts(
    claims: dict = Depends(get_current_claims),
    service: TradingAccountService = Depends(),
):
    """
    Recupera tutti i Trading Accounts dell'utente autenticato.
    """
    return await service.get_trading_accounts_for_user(claims)


@router.get("/{account_id}", response_model=TradingAccountRead)
async def get_trading_account(
    account_id: UUID,
    claims: dict = Depends(get_current_claims),
    service: TradingAccountService = Depends(),
):
    """
    Recupera un singolo Trading Account per ID.
    """
    account = await service.get_trading_account_by_id(account_id, claims)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trading Account non trovato o non appartenente all'utente.",
        )
    return account