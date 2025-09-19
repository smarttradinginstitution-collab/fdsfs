# app/Controllers/admin_controller.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.Services.snaptrade_service import SnapTradeService
from app.Infrastructure.db import get_db

router = APIRouter()

@router.get("/snaptrade-users", response_model=list[str])
async def list_snaptrade_users(db: AsyncSession = Depends(get_db)):
    """
    Returns a list of all user IDs registered with SnapTrade.
    Admin-only endpoint.
    """
    snaptrade_service = SnapTradeService(db)
    users = await snaptrade_service.list_all_snaptrade_users()
    if isinstance(users, dict) and "error" in users:
        raise HTTPException(status_code=500, detail=users["error"])
    return users
