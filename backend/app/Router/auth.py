# app/Router/auth.py
from __future__ import annotations

from uuid import UUID
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Infrastructure.supabase_client import get_supabase
from app.Repositories.user_role_repository import UserRoleRepository

bearer = HTTPBearer(auto_error=True)

async def get_current_claims(
    request: Request,
    creds: HTTPAuthorizationCredentials = Depends(bearer),
):
    """
    Legge il Bearer token dall'header Authorization e chiede a Supabase
    i dati dell'utente: supabase.auth.get_user(<token>).
    Non fa decodifica JWT locale: delega la validazione a Supabase.
    Ritorna un dict con almeno: {"sub": <user_id>, "email": <email>} 
    """
    token = creds.credentials
    sb = get_supabase()

    try:
        # Nota: supabase-py v2 -> get_user(token) ritorna un oggetto con .user
        res = sb.auth.get_user(token)
        user = res.user
        if not user:
            raise HTTPException(status_code=401, detail="Token non valido")
        # user.id è lo UUID dell'utente Supabase
        return {"sub": str(user.id), "email": user.email}
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token non valido")


def require_roles(roles: list[str]):
    """
    Dipendenza che conferma che l'utente autenticato abbia ALMENO uno dei ruoli richiesti.
    I ruoli sono nella tua tabella 'public.roles' via tabella ponte 'public.user_roles'.
    """
    async def dep(
        claims=Depends(get_current_claims),
        db: AsyncSession = Depends(get_db),
    ):
        user_id_str = claims.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=401, detail="Token senza sub")

        try:
            user_uuid = UUID(user_id_str)
        except Exception:
            raise HTTPException(status_code=401, detail="sub non è un UUID valido")

        repo = UserRoleRepository(db)
        for r in roles:
            if await repo.user_has_role(user_uuid, r):
                return claims

        raise HTTPException(status_code=403, detail="Ruolo non autorizzato")
    return dep
