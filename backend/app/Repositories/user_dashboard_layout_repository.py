# app/Repositories/user_dashboard_layout_repository.py
from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.user_dashboard_layout import UserDashboardLayout
from app.Schemas.user_dashboard_layout import (
    UserDashboardLayoutCreate,
    UserDashboardLayoutUpdate,
)


class UserDashboardLayoutRepository:
    """Encapsula l’accesso a user_dashboard_layouts (async)."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_user_id(self, user_id: UUID) -> Optional[UserDashboardLayout]:
        """Ritorna il layout per user_id."""
        q = select(UserDashboardLayout).where(UserDashboardLayout.user_id == user_id)
        res = await self.db.execute(q)
        return res.scalars().first()

    async def create(self, layout_data: UserDashboardLayoutCreate) -> UserDashboardLayout:
        """Crea un nuovo layout per un utente, verificando l'unicità."""
        existing_layout = await self.get_by_user_id(layout_data.user_id)
        if existing_layout:
            raise HTTPException(
                status_code=409,
                detail="A layout for this user already exists.",
            )

        db_layout = UserDashboardLayout(**layout_data.model_dump())
        self.db.add(db_layout)
        await self.db.commit()
        await self.db.refresh(db_layout)
        return db_layout

    async def update(
        self, db_obj: UserDashboardLayout, payload: UserDashboardLayoutUpdate
    ) -> UserDashboardLayout:
        """Aggiorna un layout esistente."""
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_obj, key, value)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
