# app/Controllers/general_account_controller.py
from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status

from app.Services.general_account_service import GeneralAccountService
from app.Schemas.general_account import GeneralAccountRead
from app.Services.auth_service import get_current_user
from app.Models.auth_user import AuthUser

router = APIRouter(
    prefix="/general-accounts",
    tags=["General Accounts"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=GeneralAccountRead, status_code=status.HTTP_201_CREATED)
def create_general_account(
    current_user: AuthUser = Depends(get_current_user),
    service: GeneralAccountService = Depends(),
):
    """
    Crea un General Account per l'utente autenticato.
    Se l'utente ha già un account, lo restituisce senza crearne uno nuovo.
    """
    # Il servizio gestisce già la logica di non creare duplicati.
    account = service.create_general_account_for_user(current_user)
    return account


@router.get("/me", response_model=GeneralAccountRead)
def get_my_general_account(
    current_user: AuthUser = Depends(get_current_user),
    service: GeneralAccountService = Depends(),
):
    """
    Recupera il General Account dell'utente autenticato.
    """
    account = service.get_general_account_for_user(current_user)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="General Account non trovato per questo utente.",
        )
    return account