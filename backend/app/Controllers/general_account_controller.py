# app/Controllers/general_account_controller.py
# Questo file contiene la logica di business per la gestione dei General Accounts.
from __future__ import annotations

from fastapi import Depends, HTTPException, status

# Importa il servizio che gestisce la logica di interazione con il database.
from app.Services.general_account_service import GeneralAccountService
# Importa la dipendenza per ottenere i dati dell'utente autenticato.
from app.Router.auth import get_current_claims


async def create_general_account(
    claims: dict = Depends(get_current_claims),
    service: GeneralAccountService = Depends(),
):
    """
    Crea un General Account per l'utente autenticato.

    Se l'utente ha già un account, il servizio lo restituirà senza crearne
    uno nuovo, garantendo l'idempotenza della creazione.
    """
    # Delega la creazione (o il recupero) dell'account al servizio.
    account = await service.create_general_account_for_user(claims)
    return account


async def get_my_general_account(
    claims: dict = Depends(get_current_claims),
    service: GeneralAccountService = Depends(),
):
    """
    Recupera il General Account associato all'utente autenticato.
    """
    # Delega il recupero dell'account al servizio.
    account = await service.get_general_account_for_user(claims)
    # Se il servizio non trova un account, solleva un'eccezione HTTP 404.
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="General Account non trovato per questo utente.",
        )
    return account