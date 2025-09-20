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

    async def list_connections(
        self,
        db: AsyncSession = Depends(get_db),
        claims: dict = Depends(get_current_claims),
    ) -> list[dict]:
        """
        Handles the request to list all connections for a user.
        """
        from app.Repositories.brokerage_connection_repository import BrokerageConnectionRepository

        user_id_str = claims.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=401, detail="Token does not contain user ID (sub).")

        svc = SnapTradeService(db)
        sync_success = await svc.synchronize_connections(user_id_str)
        if not sync_success:
            # Not raising an exception here, as we can still return the cached data.
            # The error is logged in the service.
            pass

        repo = BrokerageConnectionRepository(db)
        connections = await repo.list_by_user(uuid.UUID(user_id_str))
        return connections

    async def handle_reconnect_link(
        self,
        reconnect_request: "ReconnectRequest",
        db: AsyncSession = Depends(get_db),
        claims: dict = Depends(get_current_claims),
    ) -> dict:
        """
        Handles the request to generate a SnapTrade reconnect link.
        """
        from app.Schemas.snaptrade import ReconnectRequest

        user_id_str = claims.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=401, detail="Token does not contain user ID (sub).")

        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user ID format in token.")

        svc = SnapTradeService(db)
        result = await svc.generate_reconnect_link(user_id, reconnect_request.connection_id)

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return result
