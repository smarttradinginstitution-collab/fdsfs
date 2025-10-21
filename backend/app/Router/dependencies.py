# app/Router/dependencies.py
from __future__ import annotations

from typing import cast, List
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.Infrastructure.db import get_db
from app.Models.auth_user import AuthUser
from app.Models.general_account import GeneralAccount
from app.Router.auth import get_current_claims, require_roles
from app.Repositories.user_role_repository import UserRoleRepository


class CurrentUser:
    def __init__(
        self,
        id: UUID,
        email: str,
        roles: list[str],
        is_admin: bool,
    ):
        self.id = id
        self.email = email
        self.roles = roles
        self.is_admin = is_admin


async def get_current_user(
    claims: dict = Depends(get_current_claims),
    db: AsyncSession = Depends(get_db),
) -> CurrentUser:
    """
    Restituisce un oggetto CurrentUser contenente id, email, ruoli e un flag is_admin.
    """
    user_id_str = claims.get("sub")
    if not user_id_str:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token claim 'sub' mancante")

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token claim 'sub' non è un UUID valido")

    repo = UserRoleRepository(db)
    user_roles_models = await repo.list_user_roles(user_id)
    roles = [role.name for role in user_roles_models]
    is_admin = "admin" in roles

    return CurrentUser(id=user_id, email=cast(str, claims.get("email")), roles=roles, is_admin=is_admin)


async def get_current_general_account_id(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UUID:
    """
    Recupera il general_account_id associato all'utente corrente.
    Lancia un'eccezione 404 se non viene trovato nessun account.
    """
    stmt = select(GeneralAccount.id).where(GeneralAccount.user_id == current_user.id).limit(1)
    result = await db.execute(stmt)
    general_account_id = result.scalar_one_or_none()

    if not general_account_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nessun General Account trovato per l'utente corrente.",
        )
    return general_account_id