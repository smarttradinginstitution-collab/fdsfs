# app/Controllers/user_dashboard_layout_controller.py
from __future__ import annotations

import logging
import time
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Router.auth import get_current_claims
from app.Services.user_dashboard_layout_service import UserDashboardLayoutService
from app.Schemas.user_dashboard_layout import UserDashboardLayoutUpdate, UserDashboardLayoutRead


class UserDashboardLayoutController:
    """Controller for dashboard layout operations."""

    def __init__(self) -> None:
        ...

    async def get_user_layout(
        self,
        db: AsyncSession = Depends(get_db),
        claims: dict = Depends(get_current_claims),
    ) -> UserDashboardLayoutRead:
        """
        Retrieves the layout for the currently authenticated user.
        Raises 404 if no layout is found.
        """
        logging.basicConfig(level=logging.INFO)
        logging.info("CONTROLLER: Inizio richiesta get_user_layout")
        start_time = time.time()

        user_id = UUID(claims["sub"])
        service = UserDashboardLayoutService(db)
        layout = await service.get_layout(user_id)

        if layout is None:
            raise HTTPException(status_code=404, detail="Dashboard layout not found.")

        end_time = time.time()
        logging.info(f"CONTROLLER: Fine richiesta. Tempo totale impiegato: {end_time - start_time:.4f} secondi")
        return layout

    async def save_user_layout(
        self,
        payload: UserDashboardLayoutUpdate,
        db: AsyncSession = Depends(get_db),
        claims: dict = Depends(get_current_claims),
    ) -> UserDashboardLayoutRead:
        """
        Saves or updates the layout for the currently authenticated user.
        """
        user_id = UUID(claims["sub"])
        service = UserDashboardLayoutService(db)
        saved_layout = await service.save_layout(user_id, payload)
        return saved_layout
