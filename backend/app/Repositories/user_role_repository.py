# app/Repositories/user_role_repository.py

from __future__ import annotations

from typing import List
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.Models.role import Role
from app.Models.user_role import UserRole


class UserRoleRepository:
    """Repository per la tabella ponte user_roles e query correlate ai ruoli utente."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_user_roles(self, user_id: UUID) -> List[Role]:
        """
        Ritorna direttamente i RUOLI assegnati a user_id, tramite JOIN sul ponte.
        """
        stmt = (
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def list_role_names(self, user_id: UUID) -> List[str]:
        """
        Ritorna i nomi dei ruoli dell'utente (case esatto come a DB).
        """
        stmt = (
            select(Role.name)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
        )
        res = await self.db.execute(stmt)
        return [row[0] for row in res.all()]

    async def user_has_role(self, user_id: UUID, role_name: str) -> bool:
        """
        True se l'utente ha un ruolo con quel nome (match case-insensitive e trim).
        """
        stmt = (
            select(Role.id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(
                UserRole.user_id == user_id,
                func.lower(func.trim(Role.name)) == func.lower(func.trim(role_name)),
            )
            .limit(1)
        )
        res = await self.db.execute(stmt)
        return res.scalar() is not None

    async def assign(self, user_id: UUID, role_id: UUID) -> UserRole:
        """
        Crea l'associazione user_id ↔ role_id.
        Esegue commit e ritorna l'oggetto ponte creato.
        """
        row = UserRole(user_id=user_id, role_id=role_id)
        self.db.add(row)
        try:
            await self.db.commit()
        except IntegrityError as e:
            await self.db.rollback()
            error_detail = str(e.orig).lower()
            if "user_roles_role_id_fkey" in error_detail or "user_roles_user_id_fkey" in error_detail:
                raise HTTPException(
                    status_code=404,
                    detail="User or Role not found.",
                )
            if "unique constraint" in error_detail or "duplicate key" in error_detail:
                 raise HTTPException(
                    status_code=409,
                    detail="This role is already assigned to the user.",
                )
            # For any other integrity error, re-raise it to return a 500
            raise
        await self.db.refresh(row)
        return row

    async def unassign(self, user_id: UUID, role_id: UUID) -> bool:
        """
        Elimina l'associazione user_id ↔ role_id.
        Esegue commit. Ritorna True se almeno una riga è stata cancellata.
        """
        stmt = (
            UserRole.__table__.delete()
            .where(UserRole.user_id == user_id, UserRole.role_id == role_id)
            .execution_options(synchronize_session="fetch")
        )
        res = await self.db.execute(stmt)
        await self.db.commit()
        return (res.rowcount or 0) > 0
