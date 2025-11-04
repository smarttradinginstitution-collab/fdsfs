# app/Router/import_router.py
# Questo file definisce gli endpoint per l'importazione di file di trade.
from __future__ import annotations

from typing import List
import uuid

from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, status

# Importa le funzioni del controller che contengono la logica effettiva.
from app.Controllers import import_controller
# Importa lo schema Pydantic per la validazione dei dati di risposta.
from app.Schemas.import_run import ImportRunRead

# Definizione del router specifico per l'importazione.
router = APIRouter(
    prefix="/import",
    tags=["Import"],
)

# ==============================================================================
# ASSOCIAZIONE DELLE ROTTE AI CONTROLLER
# ==============================================================================

# Rotta per importare i trade da file CSV di Tradovate.
# Questa operazione avvia un task in background e restituisce immediatamente
# un record 'ImportRun' per tracciare lo stato.
router.post(
    "/tradovate/{trading_account_id}",
    response_model=ImportRunRead,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Import trades from Tradovate CSV files",
)(import_controller.import_tradovate_trades)

# Rotta per importare i trade da un file HTML di MT5.
# Anche questa operazione avvia un task in background.
router.post(
    "/mt5/{trading_account_id}",
    response_model=ImportRunRead,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Import trades from MT5 HTML file",
)(import_controller.import_mt5_trades)

# Rotta per verificare lo stato di un'importazione in background.
router.get(
    "/status/{import_run_id}",
    response_model=ImportRunRead,
    status_code=status.HTTP_200_OK,
    summary="Get the status of an import run",
)(import_controller.get_import_status)

# Rotta per importare i trade da un file CSV di NinjaTrader 8.
router.post(
    "/ninjatrader/{trading_account_id}",
    response_model=ImportRunRead,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Import trades from NinjaTrader 8 CSV file",
)(import_controller.import_ninjatrader_trades)