# backend/app/Controllers/import_controller.py
# Questo file contiene la logica per la gestione delle richieste di importazione.
# Le funzioni qui presenti sono chiamate dagli endpoint definiti in import_router.py.
from typing import List
import uuid

from fastapi import Depends, UploadFile, File, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession

# Importa le dipendenze e i servizi necessari.
from app.Infrastructure.db import get_db
from app.Router.auth import get_current_claims
from app.Services.import_service import ImportService

async def import_tradovate_trades(
    trading_account_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    claims: dict = Depends(get_current_claims),
):
    """
    Gestisce l'upload di uno o più file CSV di Tradovate e avvia il processo
    di importazione in background.

    - **trading_account_id**: L'ID del conto di trading a cui associare i trade.
    - **background_tasks**: Oggetto di FastAPI per aggiungere task in background.
    - **files**: Lista dei file CSV esportati da Tradovate.
    - **db**: Sessione del database.
    - **claims**: Dati dell'utente autenticato.
    """
    # Limita il numero di file che possono essere caricati contemporaneamente.
    if len(files) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot upload more than 5 files at once."
        )

    user_id = uuid.UUID(claims.get("sub"))
    import_service = ImportService(db)

    # Per semplicità, processiamo un solo file (il report di performance)
    # e creiamo un 'ImportRun' per esso.
    performance_report_file = None
    for file in files:
        if "performance" in file.filename.lower():
            performance_report_file = file
            break

    # Se il file di performance non è presente, solleva un errore.
    if not performance_report_file:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A 'Performance' report CSV file is required for the import."
        )

    # Crea un record iniziale per tracciare l'importazione.
    initial_import_run = await import_service.create_initial_import_run(
        user_id=user_id,
        trading_account_id=trading_account_id,
        file_name=performance_report_file.filename,
        source_type="csv"
    )

    # Legge il contenuto del file.
    file_content = await performance_report_file.read()

    # Aggiunge il processo di importazione a un task in background per non
    # bloccare la risposta HTTP.
    background_tasks.add_task(
        import_service.process_tradovate_import,
        import_run_id=initial_import_run.id,
        file_content=file_content,
    )

    # Restituisce immediatamente il record 'ImportRun' per il polling.
    return initial_import_run

async def import_mt5_trades(
    trading_account_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    claims: dict = Depends(get_current_claims),
):
    """
    Gestisce l'upload di un file HTML di MT5 e avvia l'importazione in background.
    """
    # Controlla che il file sia un file HTML.
    if not file.filename.lower().endswith('.html'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file must be an HTML file."
        )

    user_id = uuid.UUID(claims.get("sub"))
    import_service = ImportService(db)

    # Crea un record iniziale per tracciare l'importazione.
    initial_import_run = await import_service.create_initial_import_run(
        user_id=user_id,
        trading_account_id=trading_account_id,
        file_name=file.filename,
        source_type="html",
    )

    file_content = await file.read()

    # Aggiunge il processo di importazione a un task in background.
    background_tasks.add_task(
        import_service.process_mt5_import,
        import_run_id=initial_import_run.id,
        file_content=file_content,
    )

    return initial_import_run

async def get_import_status(
    import_run_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    claims: dict = Depends(get_current_claims),
):
    """
    Recupera lo stato corrente di un'importazione in background.
    """
    user_id = uuid.UUID(claims.get("sub"))
    import_service = ImportService(db)

    # Recupera il record dell'importazione.
    import_run = await import_service.get_import_run(import_run_id)

    if not import_run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import run not found.")

    # Controllo di sicurezza: l'utente può richiedere solo le proprie importazioni.
    if import_run.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this import run.")

    return import_run