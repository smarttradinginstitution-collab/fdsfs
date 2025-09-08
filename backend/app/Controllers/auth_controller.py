# app/Controllers/auth_controller.py

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Infrastructure import supabase_service
from app.Router.auth import get_current_claims
from app.Schemas.auth_session import (
    LoginInput,
    LoginResponse,
    RegisterInput,
    RegisterResponse,
    LogoutResponse,
)
from app.config import settings


class AuthController:
    """
    Controller per autenticazione basata su Supabase (GoTrue) usando **solo SERVICE KEY**.
    - /login: password grant (service key).
    - /register: crea utente + eventuali patch admin; in dev può auto-confermare.
    - /logout: revoca sessioni/refresh dell’utente corrente (access token rimane valido finché scade).
    """

    def __init__(self) -> None:
        ...

    async def login(
        self,
        payload: LoginInput,
        db: AsyncSession = Depends(get_db),
    ) -> LoginResponse:
        res = await supabase_service.sign_in(payload.email, payload.password)
        if res.get("error"):
            msg = res.get("message") or "Credenziali non valide"
            # Dettagli extra solo in DEV
            if settings.ENV == "dev":
                bits: list[str] = []
                if "http_status" in res:
                    bits.append(f"http_status={res['http_status']}")
                if "error_code" in res:
                    bits.append(f"error_code={res['error_code']}")
                raw = res.get("raw")
                if isinstance(raw, dict):
                    raw_msg = raw.get("message") or raw.get("error_description")
                    if raw_msg and raw_msg != msg:
                        bits.append(f"raw='{raw_msg}'")
                if bits:
                    msg = f"{msg} ({', '.join(bits)})"
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)

        if not res.get("access_token"):
            # evenienza rara, ma meglio errore chiaro
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Login upstream senza access_token",
            )

        return LoginResponse(
            access_token=res.get("access_token"),
            token_type=res.get("token_type") or "bearer",
            expires_in=res.get("expires_in"),
            refresh_token=res.get("refresh_token"),
            user=res.get("user") or {},
        )

    async def register(
        self,
        payload: RegisterInput,
        db: AsyncSession = Depends(get_db),
    ) -> RegisterResponse:
        res = await supabase_service.register_user(
            email=payload.email,
            password=payload.password,
            user_meta=payload.user_meta,
            app_meta=payload.app_meta,
            banned_until=None,
            phone=payload.phone,
        )
        if res.get("error"):
            msg = res.get("message") or "Registrazione fallita"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

        user = (res.get("user") or {})
        return RegisterResponse(
            user_id=user.get("id"),
            email=user.get("email"),
            user=user,
            status="registered",
        )

    async def logout(
        self,
        claims=Depends(get_current_claims),
        db: AsyncSession = Depends(get_db),
    ) -> LogoutResponse:
        # In DEV, se non abbiamo sub (perché non abbiamo usato un token “vero”), simuliamo OK
        user_id = claims.get("sub")
        if settings.ENV == "dev" and not user_id:
            return LogoutResponse(ok=True)

        if not user_id:
            raise HTTPException(status_code=401, detail="Token senza sub")

        res = await supabase_service.admin_logout_user(user_id)
        if res.get("error"):
            msg = res.get("message") or "Logout non riuscito"
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=msg)

        return LogoutResponse(ok=True)
