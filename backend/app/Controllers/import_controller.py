# backend/app/Controllers/import_controller.py
from typing import List
import uuid
from fastapi import Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Router.auth import get_current_claims
from app.Services.import_service import ImportService
from app.Infrastructure.storage import upload_import_file
from app.tasks import process_import_task

async def import_tradovate_trades(
    trading_account_id: uuid.UUID,
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    claims: dict = Depends(get_current_claims),
):
    """
    Gestisce l'upload di uno o più file CSV di Tradovate, li salva nello storage
    e avvia un task Celery per l'importazione in background.
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Almeno un file CSV è richiesto."
        )

    # Verifica che tutti i file siano CSV
    for file in files:
        if not file.filename.lower().endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Il file '{file.filename}' non è un CSV valido."
            )

    user_id = uuid.UUID(claims.get("sub"))
    import_service = ImportService(db)

    # Crea un'unica ImportRun per l'intero lotto di file
    file_names = ", ".join([f.filename for f in files])
    initial_import_run = await import_service.create_initial_import_run(
        user_id=user_id,
        trading_account_id=trading_account_id,
        file_name=file_names,
        source_type="csv"
    )

    # Carica tutti i file su Supabase Storage e raccoglie i loro percorsi
    storage_paths = []
    for file in files:
        path = await upload_import_file(file, initial_import_run.id)
        storage_paths.append(path)

    # Avvia un singolo task Celery per processare tutti i file
    process_import_task.delay(str(initial_import_run.id), storage_paths, "tradovate")

    return initial_import_run

async def import_mt5_trades(
    trading_account_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    claims: dict = Depends(get_current_claims),
):
    """
    Gestisce l'upload di un file HTML di MT5, lo salva nello storage
    e avvia un task Celery per l'importazione in background.
    """
    if not file.filename.lower().endswith('.html'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Il file caricato deve essere un file HTML."
        )

    user_id = uuid.UUID(claims.get("sub"))
    import_service = ImportService(db)

    initial_import_run = await import_service.create_initial_import_run(
        user_id=user_id,
        trading_account_id=trading_account_id,
        file_name=file.filename,
        source_type="html",
    )

    # Carica il file su Supabase Storage
    storage_path = await upload_import_file(file, initial_import_run.id)

    # Avvia il task Celery
    process_import_task.delay(str(initial_import_run.id), [storage_path], "mt5")

    return initial_import_run

async def get_import_status(
    import_run_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    claims: dict = Depends(get_current_claims),
):
    """
    Recupera lo stato corrente di un'importazione. L'implementazione non cambia
    poiché legge sempre lo stato dal database.
    """
    user_id = uuid.UUID(claims.get("sub"))
    import_service = ImportService(db)

    import_run = await import_service.get_import_run(import_run_id)
    if not import_run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import run not found.")

    if import_run.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this import run.")

    return import_run
