# app/Controllers/auth_controller.py

from __future__ import annotations
from uuid import UUID
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.Infrastructure.db import get_db
from app.Infrastructure import supabase_service
from app.Router.auth import get_current_claims
from app.Repositories.user_role_repository import UserRoleRepository
from app.Models.role import Role
from app.Schemas.auth_session import (
    LoginInput,
    MfaLoginInput,
    RefreshTokenInput,
    LoginResponse,
    RegisterInput,
    RegisterResponse,
    LogoutResponse,
)
from app.config import settings


class AuthController:
    """
    Controller per autenticazione basata su Supabase (GoTrue).
    Usa sempre la SERVICE ROLE KEY (SUPABASE_KEY) lato backend.
    """

    def __init__(self) -> None:
        ...

    # ------------------------------
    # LOGIN
    # ------------------------------
    async def login(
        self,
        payload: LoginInput,
        db: AsyncSession = Depends(get_db),
    ) -> LoginResponse:
        """
        Effettua il login con email + password:
        - chiama Supabase /auth/v1/token (grant_type=password).
        - se credenziali errate → 401.
        - se MFA è richiesto → 401 con detail speciale.
        - ritorna access_token + refresh_token + user info.
        """
        res = await supabase_service.sign_in(payload.email, payload.password)

        if res.get("error"):
            # Controlla se l'errore è dovuto a MFA richiesto
            raw_msg = (res.get("raw") or {}).get("error_description", "").lower()
            if "multi-factor authentication" in raw_msg:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={"mfa_required": True, "message": "MFA code is required."},
                )

            # Altrimenti, gestisci come errore di credenziali standard
            msg = res.get("message") or "Credenziali non valide"
            if settings.ENV == "dev":
                bits: list[str] = []
                if "http_status" in res:
                    bits.append(f"http_status={res['http_status']}")
                if "error_code" in res:
                    bits.append(f"error_code={res['error_code']}")
                if raw_msg and raw_msg != msg.lower():
                    bits.append(f"raw='{raw_msg}'")
                if bits:
                    msg = f"{msg} ({', '.join(bits)})"

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)

        # Supabase deve restituire almeno un access_token
        if not res.get("access_token"):
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

    # ------------------------------
    # MFA LOGIN VERIFICATION
    # ------------------------------
    async def mfa_login_verify(
        self,
        payload: MfaLoginInput,
        db: AsyncSession = Depends(get_db),
    ) -> LoginResponse:
        """
        Completa il login per un utente con MFA, fornendo il codice TOTP.
        """
        res = await supabase_service.sign_in(
            payload.email, payload.password, otp=payload.code
        )

        if res.get("error"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=res.get("message") or "Codice MFA non valido o credenziali errate.",
            )

        if not res.get("access_token"):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Login MFA upstream senza access_token",
            )

        return LoginResponse(
            access_token=res.get("access_token"),
            token_type=res.get("token_type") or "bearer",
            expires_in=res.get("expires_in"),
            refresh_token=res.get("refresh_token"),
            user=res.get("user") or {},
        )

    # ------------------------------
    # REFRESH TOKEN
    # ------------------------------
    async def refresh(
        self,
        payload: RefreshTokenInput,
    ) -> LoginResponse:
        """
        Ottiene una nuova sessione (access_token + refresh_token)
        utilizzando un refresh_token valido.
        """
        res = await supabase_service.refresh_session(payload.refresh_token)

        if res.get("error"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=res.get("message") or "Refresh token non valido o scaduto.",
            )

        if not res.get("access_token"):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Refresh upstream senza access_token",
            )

        return LoginResponse(
            access_token=res.get("access_token"),
            token_type=res.get("token_type") or "bearer",
            expires_in=res.get("expires_in"),
            refresh_token=res.get("refresh_token"),
            user=res.get("user") or {},
        )

    # ------------------------------
    # REGISTER
    # ------------------------------
    async def register(
        self,
        payload: RegisterInput,
        db: AsyncSession = Depends(get_db),
    ) -> RegisterResponse:
        """
        Crea un nuovo utente:
        - chiama Supabase per la registrazione.
        - se va a buon fine, assegna automaticamente il ruolo 'user'
          nella tabella ponte user_roles.
        """
        # 1) crea utente su Supabase
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
        user_id_str = user.get("id")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Registrazione completata ma user.id mancante dalla risposta",
            )

        # 2) trova l'id del ruolo 'user' nella tabella roles
        stmt = select(Role.id).where(Role.name.ilike("user")).limit(1)
        role_id_row = await db.execute(stmt)
        role_id = role_id_row.scalar_one_or_none()

        if role_id is None:
            # se manca il ruolo 'user' → registrazione completata ma senza ruolo
            return RegisterResponse(
                user_id=user_id_str,
                email=user.get("email"),
                user=user,
                status="registered_but_role_missing:user",
            )

        # 3) crea la riga nella tabella ponte user_roles
        repo = UserRoleRepository(db)
        try:
            await repo.assign(user_id=UUID(user_id_str), role_id=role_id)
        except IntegrityError:
            # se è già assegnato, ignoriamo
            pass

        return RegisterResponse(
            user_id=user_id_str,
            email=user.get("email"),
            user=user,
            status="registered",
        )

    # ------------------------------
    # LOGOUT
    # ------------------------------
    async def logout(
        self,
        claims=Depends(get_current_claims),
        db: AsyncSession = Depends(get_db),
    ) -> LogoutResponse:
        """
        Logout robusto:
        - prova revoca sessioni lato Supabase Admin;
        - se fallisce per errori non critici (es. utente già senza sessioni),
          NON blocca il logout lato client.
        """
        user_id = claims.get("id") or claims.get("sub")
        if not user_id:
            # Token valido ma senza id → non possiamo revocare sessioni admin.
            # Lato client il logout è comunque "butta token".
            return LogoutResponse(ok=True)

        # Chiamata Admin Supabase (service key) - best effort
        res = await supabase_service.admin_logout_user(user_id)

        if res.get("error"):
            http_status = int(res.get("http_status") or 500)
            message = res.get("message") or "Logout upstream non riuscito"

            # Errori NON critici: trattiamoli come best-effort ⇒ ok=True
            # Esempi: 400/404 (utente non trovato), 409 (nessuna sessione), 422 (id mal formattato)
            if http_status in (400, 404, 409, 422):
                # logga e continua
                # print(f"[logout] non-crit admin error {http_status}: {message}")
                return LogoutResponse(ok=True)

            # Errori critici (auth/key/permessi o server down): segnala 502
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Logout admin error {http_status}: {message}",
            )

        # Tutto ok lato admin
        return LogoutResponse(ok=True)
