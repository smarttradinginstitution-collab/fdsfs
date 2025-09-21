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


@router.get("", response_model=PaginatedActivitiesResponse)
async def get_account_activities(
    account_id: uuid.UUID,
    type: Optional[str] = Query(None, description="Filter by activity type, comma-separated (e.g., BUY,SELL,DIV)"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    claims: dict = Depends(get_current_claims)
):
    """
    Retrieves a paginated list of locally stored activities for a specific account.
    """
    # Basic permission check could be added here to ensure user owns the account

    activity_repo = ActivityRepository(db)

    type_filter = type.split(',') if type else None

    activities, total_count = await activity_repo.get_activities_paginated(
        account_id=account_id,
        type_filter=type_filter,
        limit=limit,
        offset=offset
    )

    return {
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "data": activities
    }
