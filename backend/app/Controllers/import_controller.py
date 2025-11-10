# backend/app/Controllers/import_controller.py
import uuid
import hashlib
from fastapi import Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.Infrastructure.db import get_db
from app.Router.auth import get_current_claims
from app.Services.import_service import ImportService
from app.Infrastructure.storage import upload_import_file
from app.tasks import process_import_task

async def import_tradovate_trades(
    trading_account_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    claims: dict = Depends(get_current_claims),
):
    """
    Gestisce l'upload di un singolo file CSV di Tradovate.
    """
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Il file deve essere in formato CSV."
        )

    user_id = uuid.UUID(claims.get("sub"))
    import_service = ImportService(db)

    # Legge il contenuto del file per calcolare l'hash
    file_content = await file.read()
    await file.seek(0) # Riporta il puntatore all'inizio del file per l'upload
    file_hash = hashlib.sha256(file_content).hexdigest()

    import_run, created = await import_service.get_or_create_import_run(
        user_id=user_id,
        trading_account_id=trading_account_id,
        file_name=file.filename,
        file_hash=file_hash,
        source_type="csv"
    )

    if created:
        # Se la run è stata appena creata, procedi con l'upload e l'accodamento
        storage_path = await upload_import_file(file, import_run.id)
        process_import_task.delay(str(import_run.id), storage_path, "tradovate")

    return import_run


async def import_mt5_trades(
    trading_account_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    claims: dict = Depends(get_current_claims),
):
    """
    Gestisce l'upload di un file HTML di MT5.
    """
    if not file.filename.lower().endswith('.html'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Il file caricato deve essere un file HTML."
        )

    user_id = uuid.UUID(claims.get("sub"))
    import_service = ImportService(db)

    file_content = await file.read()
    await file.seek(0)
    file_hash = hashlib.sha256(file_content).hexdigest()

    import_run, created = await import_service.get_or_create_import_run(
        user_id=user_id,
        trading_account_id=trading_account_id,
        file_name=file.filename,
        file_hash=file_hash,
        source_type="html",
    )

    if created:
        storage_path = await upload_import_file(file, import_run.id)
        process_import_task.delay(str(import_run.id), storage_path, "mt5")

    return import_run


async def get_import_status(
    import_run_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    claims: dict = Depends(get_current_claims),
):
    """
    Recupera lo stato corrente di un'importazione.
    """
    user_id = uuid.UUID(claims.get("sub"))
    import_service = ImportService(db)

    import_run = await import_service.get_import_run(import_run_id)
    if not import_run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import run not found.")

    if import_run.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this import run.")

    return import_run
