# app/Router/auth.py
from __future__ import annotations

from uuid import UUID
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Services.jwt_service import get_jwks, validate_token_local
from app.Repositories.user_role_repository import UserRoleRepository

bearer = HTTPBearer(auto_error=True)

async def get_current_claims(
    request: Request,
    creds: HTTPAuthorizationCredentials = Depends(bearer),
):
    """
    Valida il token JWT localmente usando le chiavi JWKS in cache per
    evitare chiamate di rete lente a Supabase.
    Ritorna il payload del token decodificato.
    """
    token = creds.credentials
    jwks = await get_jwks()
    payload = validate_token_local(token, jwks)
    return payload


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
