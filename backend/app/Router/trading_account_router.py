# app/Router/trading_account_router.py
# Questo file definisce gli endpoint per la gestione dei Trading Accounts.
from __future__ import annotations

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status

# Importa le funzioni del controller che gestiscono la logica.
from app.Controllers import trading_account_controller
# Importa gli schemi Pydantic per la validazione dei dati.
from app.Schemas.trading_account import TradingAccountRead, TradingAccountCreate
# Importa la dipendenza per ottenere l'utente autenticato.
from app.Router.auth import get_current_claims

# Definizione del router specifico per i Trading Accounts.
router = APIRouter(
    prefix="/trading-accounts",
    tags=["Trading Accounts"],
    responses={404: {"description": "Not found"}},
)

# ==============================================================================
# ASSOCIAZIONE DELLE ROTTE AI CONTROLLER
# ==============================================================================

# Rotta per creare un nuovo Trading Account per l'utente autenticato.
router.post(
    "/",
    response_model=TradingAccountRead,
    status_code=status.HTTP_201_CREATED,
)(trading_account_controller.create_trading_account)

# Rotta per recuperare tutti i Trading Accounts dell'utente autenticato.
router.get("/", response_model=List[TradingAccountRead])(
    trading_account_controller.get_my_trading_accounts
)

# Rotta per recuperare un singolo Trading Account tramite il suo ID.
router.get("/{account_id}", response_model=TradingAccountRead)(
    trading_account_controller.get_trading_account
)

# ==============================================================================
# ROUTER PER OPERAZIONI CONTESTUALI DELL'UTENTE ("ME")
# ==============================================================================

# Definisce un router separato per le operazioni che agiscono sul contesto
# dell'utente loggato, per avere URL più puliti come /me/trading-accounts.
router_me = APIRouter(
    prefix="/me/trading-accounts",
    tags=["Trading Accounts"],
    dependencies=[Depends(get_current_claims)],
    responses={404: {"description": "Not found"}},
)

# Rotta per aggiornare la selezione dei Trading Accounts.
router_me.put("/selection", status_code=status.HTTP_200_OK)(
    trading_account_controller.update_my_trading_accounts_selection
)