import uuid
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Models.auth_user import AuthUser
from app.Router.auth import get_current_claims
from app.Repositories.activity_repository import ActivityRepository
from app.Schemas.snaptrade import AccountActivityCreate # Re-using this for now, will refine if needed
from app.Models.account_activity import AccountActivity

router = APIRouter(tags=["Account Activities"])

# Define a response model to avoid leaking model details
class AccountActivityRead(AccountActivityCreate):
    # This inherits all fields from AccountActivityCreate
    # We can add relationship fields here if we decide to eager load them
    class Config:
        from_attributes = True

class PaginatedActivitiesResponse(BaseModel):
    total: int
    limit: int
    offset: int
    data: List[AccountActivityRead]


@router.post("/sync", status_code=status.HTTP_202_ACCEPTED)
async def sync_account_activities(
    account_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    claims: dict = Depends(get_current_claims)
):
    """
    Initiates a background task to synchronize historical activities for a specific account.
    """
    user_id_str = claims.get("sub")
    if not user_id_str:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token does not contain user ID.")

    user_id = uuid.UUID(user_id_str)
    snaptrade_service = SnapTradeService(db)

    # Add the long-running task to the background
    background_tasks.add_task(
        snaptrade_service.sync_account_activities,
        user_id=user_id,
        account_id=account_id
    )

    return {"message": "Activity synchronization has been initiated."}


# Additional imports for smart sync
from datetime import datetime, timezone, timedelta
from app.Repositories.brokerage_account_repository import BrokerageAccountRepository
from app.Services.snaptrade_service import SnapTradeService

@router.get("", response_model=PaginatedActivitiesResponse)
async def get_account_activities(
    account_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    type: Optional[str] = Query(None, description="Filter by activity type, comma-separated (e.g., BUY,SELL,DIV)"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    claims: dict = Depends(get_current_claims)
):
    """
    Retrieves a paginated list of locally stored activities for a specific account.

    This endpoint implements a "smart sync" strategy:
    - It immediately returns locally stored data.
    - If the data is older than 30 minutes, it triggers a background sync.
    """
    user_id_str = claims.get("sub")
    if not user_id_str:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token does not contain user ID.")
    user_id = uuid.UUID(user_id_str)

    # Smart Sync Logic
    account_repo = BrokerageAccountRepository(db)
    account = await account_repo.get_by_id(account_id)

    # Permission check
    if not account or account.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found or permission denied.")

    needs_sync = False
    if account.last_activities_synced_at is None:
        needs_sync = True
    else:
        time_since_last_sync = datetime.now(timezone.utc) - account.last_activities_synced_at
        if time_since_last_sync > timedelta(minutes=30):
            needs_sync = True

    if needs_sync:
        print(f"Stale activity data for account {account_id}. Triggering background sync.")
        snaptrade_service = SnapTradeService(db)
        background_tasks.add_task(
            snaptrade_service.sync_account_activities,
            user_id=user_id,
            account_id=account_id
        )

    # Always fetch and return local data immediately
    activity_repo = ActivityRepository(db)
    type_filter = type.split(',') if type else None

    activities, total_count = await activity_repo.get_activities_paginated(
        account_id=account_id,
        type_filter=type_filter,
        limit=limit,
        offset=offset
    )

    # Manually convert models to dictionaries for the response
    # because the relationship fields are commented out in the model.
    activities_list = [
        {
            "id": act.id, "user_id": act.user_id, "account_id": act.account_id,
            "security_id": act.security_id, "option_symbol_id": act.option_symbol_id,
            "type": act.type, "option_type": act.option_type, "price": act.price,
            "units": act.units, "amount": act.amount, "description": act.description,
            "trade_date": act.trade_date, "settlement_date": act.settlement_date,
            "fee": act.fee, "fx_rate": act.fx_rate, "institution": act.institution,
            "external_reference_id": act.external_reference_id
        } for act in activities
    ]

    return {
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "data": activities_list
    }
