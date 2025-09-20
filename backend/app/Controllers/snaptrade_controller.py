# app/Controllers/snaptrade_controller.py

from fastapi import Depends, HTTPException, Response, status, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from app.Infrastructure.db import get_db, SessionLocal
from app.Services.snaptrade_service import SnapTradeService, SnapTradeConnectionError, RateLimitExceededError
import uuid
import sys
from app.Router.auth import get_current_claims

async def run_background_sync(user_id: str):
    """
    A session-aware background task to synchronize SnapTrade connections for a user.
    """
    print(f"Background sync triggered for user {user_id}")
    async with SessionLocal() as db_session:
        try:
            # Note: The service now manages its own session for this background task.
            svc = SnapTradeService(db_session)
            await svc.synchronize_connections(user_id)
            print(f"Background sync finished successfully for user {user_id}")
        except Exception as e:
            # It's good practice to log errors in background tasks
            print(f"Error during background sync for user {user_id}: {e}", file=sys.stderr)


class SnapTradeController:
    async def handle_sync_connections(
        self,
        db: AsyncSession = Depends(get_db),
        claims: dict = Depends(get_current_claims),
    ) -> dict:
        """
        Handles the request to synchronously pull all connections from SnapTrade
        and update the local database.
        """
        user_id_str = claims.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=401, detail="Token does not contain user ID (sub).")

        svc = SnapTradeService(db)
        success = await svc.synchronize_connections(user_id_str)

        if not success:
            raise HTTPException(
                status_code=500,
                detail="An error occurred during connection synchronization. Check logs for details."
            )

        return {"status": "completed"}
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
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_db),
        claims: dict = Depends(get_current_claims),
    ) -> list[dict]:
        """
        Handles the request to list all connections for a user.
        It immediately returns local data and triggers a background sync if the data is stale.
        """
        from app.Repositories.brokerage_connection_repository import BrokerageConnectionRepository
        from app.Repositories.auth_user_repository import AuthUserRepository

        user_id_str = claims.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=401, detail="Token does not contain user ID (sub).")

        user_id = uuid.UUID(user_id_str)

        # Check if a background sync is needed
        user_repo = AuthUserRepository(db)
        user = await user_repo.get(user_id)

        should_sync = False
        if user and user.profile:
            if user.profile.last_synced_at is None:
                should_sync = True
            else:
                # Sync if last sync was more than 1 hour ago
                time_since_sync = datetime.now(timezone.utc) - user.profile.last_synced_at
                if time_since_sync > timedelta(hours=1):
                    should_sync = True

        if should_sync:
            # Use the new session-aware background task
            background_tasks.add_task(run_background_sync, user_id=user_id_str)

        # Immediately return data from the local database
        repo = BrokerageConnectionRepository(db)
        connections = await repo.list_by_user(user_id)
        return connections

    async def get_accounts(
        self,
        connection_id: uuid.UUID | None = None,
        db: AsyncSession = Depends(get_db),
        claims: dict = Depends(get_current_claims),
    ) -> dict:
        """
        Handles the request to list all trading accounts for a user.
        Triggers a sync with SnapTrade and returns the locally stored accounts.
        """
        user_id_str = claims.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token does not contain user ID.")

        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format in token.")

        svc = SnapTradeService(db)
        try:
            result = await svc.sync_and_get_user_accounts(user_id=user_id, connection_id=connection_id)
            return result
        except SnapTradeConnectionError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def handle_get_connection_details(
        self,
        connection_id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
        claims: dict = Depends(get_current_claims),
    ):
        """
        Handles the request to get and refresh details for a single SnapTrade connection.
        """
        user_id_str = claims.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=401, detail="Token does not contain user ID (sub).")

        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user ID format in token.")

        svc = SnapTradeService(db)
        try:
            connection = await svc.get_and_refresh_connection_details(user_id, connection_id)
            return connection
        except SnapTradeConnectionError as e:
            if "permission denied" in str(e):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found.")
            else:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def handle_refresh_connection(
        self,
        connection_id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
        claims: dict = Depends(get_current_claims),
    ) -> dict:
        """
        Handles the request to refresh a SnapTrade connection's holdings.
        """
        user_id_str = claims.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token does not contain user ID (sub).")

        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format in token.")

        svc = SnapTradeService(db)
        try:
            result = await svc.refresh_connection_holdings(user_id, connection_id)
            return result
        except RateLimitExceededError as e:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))
        except SnapTradeConnectionError as e:
            if "permission denied" in str(e):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found.")
            else:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        except Exception as e:
            # Catch any other unexpected errors
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def handle_delete_connection(
        self,
        connection_id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
        claims: dict = Depends(get_current_claims),
    ) -> Response:
        """
        Handles the request to delete a SnapTrade connection.
        """
        user_id_str = claims.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=401, detail="Token does not contain user ID (sub).")

        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user ID format in token.")

        svc = SnapTradeService(db)
        try:
            await svc.delete_connection(user_id, connection_id)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        except SnapTradeConnectionError as e:
            if "permission denied" in str(e):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found.")
            else:
                # As per user request, log the error and return a 500
                error_content = {
                    "success": False,
                    "message": "Impossibile cancellare la connessione in questo momento. Il fornitore esterno potrebbe non rispondere. Riprova più tardi."
                }
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=error_content
                )
        except Exception as e:
            # Catch any other unexpected errors
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

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
