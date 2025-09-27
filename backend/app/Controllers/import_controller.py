# backend/app/Controllers/import_controller.py
from typing import List
import uuid

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Router.auth import get_current_claims
from app.Schemas.import_run import ImportRunRead
from app.Services.import_service import ImportService
from app.Models.enums import ImportSourceType

router = APIRouter(
    prefix="/api/v1/import",
    tags=["Import"],
)

@router.post(
    "/file/{trading_account_id}",
    response_model=ImportRunRead,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Import trades from a file (Tradovate CSV or MT5 HTML)"
)
async def import_trades_from_file(
    trading_account_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    claims: dict = Depends(get_current_claims),
):
    """
    Uploads a file to import trades.

    This endpoint accepts the file and queues it for processing in the background.
    It automatically detects the file type (Tradovate CSV or MT5 HTML) and uses the appropriate parser.
    It immediately returns an initial `ImportRun` record. The status of this
    run can be polled to check the progress of the import.

    - **trading_account_id**: The ID of the trading account to associate the trades with.
    - **file**: The CSV or HTML file to import.
    """
    user_id = uuid.UUID(claims.get("sub"))
    import_service = ImportService(db)

    # Determine the source type based on the file's content type or extension
    source_type = None
    if file.content_type == 'text/csv' or file.filename.lower().endswith('.csv'):
        source_type = ImportSourceType.CSV
    elif file.content_type == 'text/html' or file.filename.lower().endswith(('.html', '.htm')):
        source_type = ImportSourceType.HTML

    if source_type is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type: {file.content_type or file.filename}. Please upload a Tradovate CSV or an MT5 HTML file."
        )

    if source_type == ImportSourceType.CSV and "performance" not in file.filename.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="For Tradovate imports, a 'Performance' report CSV file is required."
        )

    initial_import_run = await import_service.create_initial_import_run(
        user_id=user_id,
        trading_account_id=trading_account_id,
        file_name=file.filename,
        source_type=source_type
    )

    file_content = await file.read()

    # Add the processing to a background task
    background_tasks.add_task(
        import_service.process_import,
        import_run_id=initial_import_run.id,
        file_content=file_content,
    )

    return initial_import_run

@router.get(
    "/status/{import_run_id}",
    response_model=ImportRunRead,
    status_code=status.HTTP_200_OK,
    summary="Get the status of an import run"
)
async def get_import_status(
    import_run_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    claims: dict = Depends(get_current_claims),
):
    """
    Retrieves the current status of a background import process.
    """
    user_id = uuid.UUID(claims.get("sub"))
    import_service = ImportService(db)

    import_run = await import_service.get_import_run(import_run_id)

    if not import_run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import run not found.")

    # Security check: ensure the user is requesting their own import run
    if import_run.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this import run.")

    return import_run