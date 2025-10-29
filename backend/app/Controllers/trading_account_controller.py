# app/Controllers/trading_account_controller.py
# Questo file contiene la logica di business per la gestione dei Trading Accounts.
# app/Controllers/trading_account_controller.py
# Questo file contiene la logica di business per la gestione dei Trading Accounts.
from __future__ import annotations

from typing import List
from uuid import UUID
from fastapi import Depends, HTTPException, status

# Importa il servizio che gestisce la logica di interazione con il database.
from app.Services.trading_account_service import TradingAccountService
# Importa gli schemi Pydantic per la validazione dei dati.
from app.Schemas.trading_account import (
    TradingAccountCreate,
    TradingAccountSelectionUpdate,
    TradingAccountRead,
)
# Importa la dipendenza per ottenere i dati dell'utente autenticato.
from app.Router.auth import get_current_claims


async def create_trading_account(
    account_data: TradingAccountCreate,
    claims: dict = Depends(get_current_claims),
    service: TradingAccountService = Depends(),
):
    """
    Crea un nuovo Trading Account per l'utente autenticato.
    """
    # Delega la creazione dell'account al servizio.
    return await service.create_trading_account_for_user(claims, account_data)


async def get_my_trading_accounts(
    claims: dict = Depends(get_current_claims),
    service: TradingAccountService = Depends(),
):
    """
    Recupera tutti i Trading Accounts associati all'utente autenticato.
    """
    # Delega il recupero della lista di account al servizio.
    return await service.get_trading_accounts_for_user(claims)


async def get_trading_account(
    account_id: UUID,
    claims: dict = Depends(get_current_claims),
    service: TradingAccountService = Depends(),
):
    """
    Recupera un singolo Trading Account per ID, verificando la proprietà.
    """
    # Delega il recupero del singolo account al servizio.
    account = await service.get_trading_account_by_id(account_id, claims)
    # Se il servizio non trova l'account o l'utente non è autorizzato,
    # solleva un'eccezione HTTP 404.
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trading Account non trovato o non appartenente all'utente.",
        )
    return account


async def update_my_trading_account_selection(
    selection_data: TradingAccountSelectionUpdate,
    claims: dict = Depends(get_current_claims),
    service: TradingAccountService = Depends(),
) -> List[TradingAccountRead]:
    """
    Aggiorna la selezione degli account e restituisce l'elenco aggiornato.
    """
    # Il servizio ora restituisce l'elenco aggiornato, che viene passato
    # direttamente come risposta JSON con uno status 200 OK.
    return await service.update_selection_for_user(
        claims=claims, selected_ids=selection_data.trading_account_ids
    )