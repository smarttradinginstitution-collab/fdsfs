# app/Repositories/user_dashboard_layout_repository.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.user_dashboard_layout import UserDashboardLayout
from app.Schemas.user_dashboard_layout import UserDashboardLayoutUpdate


class UserDashboardLayoutRepository:
    """Encapsula l’accesso a user_dashboard_layouts (async)."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_user_id(self, user_id: UUID) -> Optional[UserDashboardLayout]:
        """Ritorna il layout per user_id."""
        q = select(UserDashboardLayout).where(UserDashboardLayout.user_id == user_id)
        res = await self.db.execute(q)
        return res.scalars().first()

    async def upsert(
        self, user_id: UUID, payload: UserDashboardLayoutUpdate
    ) -> UserDashboardLayout:
        """
        Crea o aggiorna il layout per un utente.
        Usa INSERT ... ON CONFLICT per un'operazione atomica.
        """
        insert_data = {
            "user_id": user_id,
            "layout": payload.layout,
        }
        stmt = insert(UserDashboardLayout).values(**insert_data)

        # Su conflitto (stesso user_id), aggiorna il campo 'layout' e 'updated_at'
        stmt = stmt.on_conflict_do_update(
            index_elements=[UserDashboardLayout.user_id],
            set_={
                "layout": stmt.excluded.layout,
                "updated_at": datetime.now(timezone.utc),
            },
        ).returning(UserDashboardLayout)

        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.scalar_one()
