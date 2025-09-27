# backend/app/Controllers/import_controller.py
from typing import List
import uuid

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Models.enums import ImportSourceType
from app.Router.auth import get_current_claims
from app.Schemas.import_run import ImportRunRead
from app.Services.import_service import ImportService

router = APIRouter(
    prefix="/api/v1/import",
    tags=["Import"],
)

@router.post(
    "/tradovate/{trading_account_id}",
    response_model=ImportRunRead,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Import trades from Tradovate CSV files"
)
async def import_tradovate_trades(
    trading_account_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    claims: dict = Depends(get_current_claims),
):
    """
    Uploads one or more Tradovate CSV files to import trades.

    This endpoint accepts the files and queues them for processing in the background.
    It immediately returns an initial `ImportRun` record. The status of this
    run can be polled to check the progress of the import.

    - **trading_account_id**: The ID of the trading account to associate the trades with.
    - **files**: The CSV files exported from Tradovate.
    """
    if len(files) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot upload more than 5 files at once."
        )

    user_id = uuid.UUID(claims.get("sub"))
    import_service = ImportService(db)

    # For simplicity, we process one file at a time and create one run per file.
    # A more advanced implementation could create a single "batch" run for all files.
    # We will focus on the most common case: uploading the Performance report.

    performance_report_file = None
    for file in files:
        if "performance" in file.filename.lower():
            performance_report_file = file
            break

    if not performance_report_file:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A 'Performance' report CSV file is required for the import."
        )

    initial_import_run = await import_service.create_initial_import_run(
        user_id=user_id,
        trading_account_id=trading_account_id,
        file_name=performance_report_file.filename,
        source_type=ImportSourceType.TRADOVATE_CSV,
    )

    file_content = await performance_report_file.read()

    # Add the processing to a background task
    background_tasks.add_task(
        import_service.process_tradovate_import,
        import_run_id=initial_import_run.id,
        file_content=file_content,
    )

    return initial_import_run

@router.post(
    "/mt5/{trading_account_id}",
    response_model=ImportRunRead,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Import trades from MT5 HTML files"
)
async def import_mt5_trades(
    trading_account_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    claims: dict = Depends(get_current_claims),
):
    """
    Uploads an MT5 HTML file to import trades.

    This endpoint accepts the file and queues it for processing in the background.
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An HTML file is required for the import."
        )

    # MT5 import expects a single file
    if len(files) > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only one file can be uploaded at a time for MT5 import."
        )

    html_file = files[0]
    if not html_file.filename.lower().endswith('.html'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file must be an HTML file."
        )

    user_id = uuid.UUID(claims.get("sub"))
    import_service = ImportService(db)

    initial_import_run = await import_service.create_initial_import_run(
        user_id=user_id,
        trading_account_id=trading_account_id,
        file_name=html_file.filename,
        source_type=ImportSourceType.MT5_HTML,
    )

    file_content = await html_file.read()

    background_tasks.add_task(
        import_service.process_mt5_import,
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