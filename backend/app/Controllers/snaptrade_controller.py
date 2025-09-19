# app/Controllers/snaptrade_controller.py

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.Infrastructure.db import get_db
from app.Services.snaptrade_service import SnapTradeService
import uuid
from app.Router.auth import get_current_claims

class SnapTradeController:
    def __init__(self):
        ...

    async def handle_register_user(
        self,
        db: AsyncSession = Depends(get_db),
        claims: dict = Depends(get_current_claims),
    ) -> dict:
        """
        Handles the request to register a user with SnapTrade.
        """
        user_id_str = claims.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=401, detail="Token does not contain user ID (sub).")

        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user ID format in token.")

        svc = SnapTradeService(db)
        result = await svc.register_snaptrade_user(user_id)

        if "error" in result:
            if "not found" in result["error"]:
                raise HTTPException(status_code=404, detail=result["error"])
            else:
                raise HTTPException(status_code=400, detail=result["error"])

        return result

    async def handle_generate_connection_link(
        self,
        db: AsyncSession = Depends(get_db),
        claims: dict = Depends(get_current_claims),
    ) -> dict:
        """
        Handles the request to generate a SnapTrade connection link.
        """
        user_id_str = claims.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=401, detail="Token does not contain user ID (sub).")

        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user ID format in token.")

        svc = SnapTradeService(db)
        result = await svc.generate_connection_link(user_id)

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return result
