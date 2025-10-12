# app/Controllers/general_account_controller.py
# Questo file contiene la logica di business per la gestione dei General Accounts.
from __future__ import annotations
from uuid import UUID

from fastapi import Depends, HTTPException, status, Response

# Importa i servizi necessari.
from app.Services.general_account_service import GeneralAccountService
from app.Services.notebook_service import NotebookService
# Importa la dipendenza per ottenere i dati dell'utente autenticato.
from app.Router.auth import get_current_claims
from app.Services.tags_group_service import TagsGroupService
from app.Services.tag_service import TagService


async def create_general_account(
    response: Response,
    claims: dict = Depends(get_current_claims),
    service: GeneralAccountService = Depends(),
    notebook_service: NotebookService = Depends(),
    tags_group_service: TagsGroupService = Depends(),
    tag_service: TagService = Depends(),
):
    """
    Crea un General Account per l'utente autenticato.

    Se l'utente ha già un account, il servizio lo restituirà senza crearne
    uno nuovo, garantendo l'idempotenza della creazione.
    """
    # Delega la creazione (o il recupero) dell'account al servizio.
    account, created = await service.create_general_account_for_user(
        claims=claims,
        notebook_service=notebook_service,
        tags_group_service=tags_group_service,
        tag_service=tag_service,
    )
    if created:
        response.status_code = status.HTTP_201_CREATED

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


async def get_general_account_with_all_data(
    account_id: UUID,
    claims: dict = Depends(get_current_claims),
    service: GeneralAccountService = Depends(),
):
    """
    Recupera un General Account con tutte le sue relazioni (mistakes, news, ecc.).
    """
    account = await service.get_general_account_with_all_data(
        account_id=account_id, claims=claims
    )
    return account