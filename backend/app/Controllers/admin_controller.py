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

@router.delete("/snaptrade-users/{user_id}", status_code=200)
async def delete_snaptrade_user(user_id: str, db: AsyncSession = Depends(get_db)):
    """
    Deletes a SnapTrade user and clears their secret.
    Admin-only endpoint.
    """
    snaptrade_service = SnapTradeService(db)
    result = await snaptrade_service.delete_snaptrade_user(user_id)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@router.post("/snaptrade-users/{user_id}/rotate-secret", status_code=200)
async def rotate_secret(user_id: str, db: AsyncSession = Depends(get_db)):
    """
    Rotates a SnapTrade user's secret.
    Admin-only endpoint.
    """
    snaptrade_service = SnapTradeService(db)
    result = await snaptrade_service.rotate_snaptrade_user_secret(user_id)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result
