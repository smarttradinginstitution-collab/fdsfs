# app/Router/general_account_router.py
# Questo file definisce gli endpoint per la gestione dei General Accounts.
from __future__ import annotations

from fastapi import APIRouter, Depends, status

# Importa le funzioni del controller che gestiscono la logica.
from app.Controllers import general_account_controller
# Importa gli schemi Pydantic per la validazione dei dati.
from app.Schemas.general_account import GeneralAccountRead, GeneralAccountWithData
# Importa la dipendenza per ottenere l'utente autenticato.
from app.Router.auth import get_current_claims

# Definizione del router specifico per i General Accounts.
router = APIRouter(
    prefix="/general-accounts",
    tags=["General Accounts"],
    responses={404: {"description": "Not found"}},
)

# Rotta per creare un General Account per l'utente corrente.
# Se esiste già, restituisce quello esistente.
router.post(
    "/",
    response_model=GeneralAccountRead,
    status_code=status.HTTP_201_CREATED,
)(general_account_controller.create_general_account)

# Rotta per recuperare il General Account dell'utente corrente.
router.get("/me", response_model=GeneralAccountRead)(
    general_account_controller.get_my_general_account
)

# Router per l'endpoint specifico con dati completi
router_with_data = APIRouter(
    tags=["General Accounts"],
)

router_with_data.get(
    "/general-account-with-data/{account_id}",
    response_model=GeneralAccountWithData,
    summary="Get General Account with All Data",
    description="""Recupera un General Account specifico tramite ID,
    includendo tutte le relazioni come mistakes, news impacts,
    psychology states e tags groups (con i relativi tags).""",
)(general_account_controller.get_general_account_with_all_data)