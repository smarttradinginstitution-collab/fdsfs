# app/Controllers/general_account_controller.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.Services.general_account_service import GeneralAccountService
from app.Schemas.general_account import GeneralAccountRead
from app.Router.auth import get_current_claims

router = APIRouter(
    prefix="/general-accounts",
    tags=["General Accounts"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=GeneralAccountRead, status_code=status.HTTP_201_CREATED)
async def create_general_account(
    claims: dict = Depends(get_current_claims),
    service: GeneralAccountService = Depends(),
):
    """
    Crea un General Account per l'utente autenticato.
    Se l'utente ha già un account, lo restituisce senza crearne uno nuovo.
    """
    account = await service.create_general_account_for_user(claims)
    return account


@router.get("/me", response_model=GeneralAccountRead)
async def get_my_general_account(
    claims: dict = Depends(get_current_claims),
    service: GeneralAccountService = Depends(),
):
    """
    Recupera il General Account dell'utente autenticato.
    """
    account = await service.get_general_account_for_user(claims)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="General Account non trovato per questo utente.",
        )
    return account