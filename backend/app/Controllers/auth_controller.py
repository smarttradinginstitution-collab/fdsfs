from __future__ import annotations
from uuid import UUID
from fastapi import Depends, HTTPException, status, Path
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from jose import jwt

from app.Infrastructure.db import get_db
from app.Infrastructure import supabase_service
from app.Router.auth import get_current_claims
from app.Repositories.user_role_repository import UserRoleRepository
from app.Models.role import Role
from app.Schemas.auth_session import (
    LoginInput,
    LoginResponse,
    RegisterInput,
    RegisterResponse,
    LogoutResponse,
    LoginMfaChallenge,
    VerifyMfaInput,
    VerifyMfaResponse,
    TotpEnrollInput,
    TotpEnrollResponse,
    ListFactorsResponse,
    MfaDisableInput,
)
from app.config import settings

bearer = HTTPBearer(auto_error=True)

class AuthController:
    def __init__(self) -> None:
        ...

    # LOGIN → AAL1 o MFA challenge
    async def login(self, payload: LoginInput) -> LoginResponse | LoginMfaChallenge:
        res = await supabase_service.sign_in(payload.email, payload.password)
        if res.get("error"):
            raise HTTPException(status_code=401, detail=res.get("message") or "Credenziali non valide")

        access_token = res.get("access_token")
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Login upstream non riuscito: access_token mancante",
            )
        user_obj = res.get("user") or {}

        # --- LOGICA MFA BASATA SU AAL ---
        aal = None
        try:
            decoded_token = jwt.get_unverified_claims(access_token)
            aal = decoded_token.get("aal")
        except Exception as e:
            print(f"DEBUG: Errore durante la decodifica del token: {e}")
            pass

        factors = user_obj.get("factors")

        print("--- DEBUG LOGIN MFA ---")
        print(f"AAL Level: {aal}")
        print(f"User Object: {user_obj}")
        print(f"Factors: {factors}")
        print("-----------------------")

        if aal == "aal1" and factors and len(factors) > 0:
            totp_factor = next((f for f in factors if f.get("factor_type") == "totp" and f.get("status") == "verified"), None)

            if totp_factor and access_token:
                factor_id = totp_factor.get("id")
                chal = await supabase_service.create_mfa_challenge(access_token, factor_id)

                if chal.get("error"):
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"Impossibile creare la MFA challenge: {chal.get('message')}"
                    )

                challenge_id = chal.get("id")
                if challenge_id:
                    return LoginMfaChallenge(
                        status="mfa_required",
                        access_token=access_token,
                        factor_id=factor_id,
                        challenge_id=challenge_id,
                    )

        return LoginResponse(
            access_token=access_token,
            token_type=res.get("token_type"),
            expires_in=res.get("expires_in"),
            refresh_token=res.get("refresh_token"),
            user=user_obj,
        )

    # VERIFY MFA
    async def verify_mfa(self, payload: VerifyMfaInput) -> VerifyMfaResponse:
        res = await supabase_service.verify_mfa_challenge(
            payload.access_token, payload.factor_id, payload.challenge_id, payload.code
        )
        if res.get("error"):
            raise HTTPException(status_code=401, detail=res.get("message") or "Codice OTP non valido")

        return VerifyMfaResponse(
            access_token=res.get("access_token") or payload.access_token,
            token_type=res.get("token_type") or "bearer",
            expires_in=res.get("expires_in"),
            refresh_token=res.get("refresh_token"),
            user=res.get("user") or {"mfa_status": "verified"},
        )

    # ENROLL TOTP (con challenge immediata)
    async def enroll_totp(
        self,
        payload: TotpEnrollInput | None = None,
        creds: HTTPAuthorizationCredentials = Depends(bearer),
    ) -> TotpEnrollResponse:
        access_token = creds.credentials
        user_res = await supabase_service.get_user_from_access_token(access_token)
        if user_res.get("error"):
            raise HTTPException(status_code=401, detail="Token non valido o scaduto.")

        if not user_res.get("email_confirmed_at"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Per abilitare l'MFA, devi prima confermare il tuo indirizzo email."
            )

        friendly = payload.friendly_name if payload else "Authenticator"
        res = await supabase_service.enroll_totp(access_token, friendly_name=friendly)
        if res.get("error"):
            detail = res.get("message") or "Errore sconosciuto durante l'enrollment MFA."
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

        factor_id = res.get("id")
        if not factor_id:
            raise HTTPException(status_code=502, detail="Enroll riuscito ma senza factor_id")

        totp = res.get("totp") or {}
        chal = await supabase_service.create_mfa_challenge(access_token, factor_id)
        challenge_id = chal.get("id")

        return TotpEnrollResponse(
            factor_id=factor_id,
            secret=totp.get("secret"),
            otpauth_uri=totp.get("uri"),
            qr_code=totp.get("qr_code"),
            challenge_id=challenge_id,
        )

    # LIST FACTORS
    async def list_factors(
        self, creds: HTTPAuthorizationCredentials = Depends(bearer)
    ) -> ListFactorsResponse:
        res = await supabase_service.list_factors(creds.credentials)
        if res.get("error"):
            raw = res.get("text") or res.get("message") or "List factors non riuscito"
            raise HTTPException(status_code=400, detail=raw)
        return ListFactorsResponse(factors=res.get("factors", []))

    # DELETE FACTOR
    async def delete_factor(
        self,
        factor_id: str = Path(..., description="ID del fattore TOTP da eliminare"),
        creds: HTTPAuthorizationCredentials = Depends(bearer),
    ) -> LogoutResponse:
        access_token = creds.credentials
        res = await supabase_service.delete_mfa_factor(access_token, factor_id)
        if isinstance(res, dict) and res.get("error"):
            status_code = int(res.get("http_status") or 400)
            msg = res.get("message") or res.get("msg") or "Delete factor non riuscito"
            raise HTTPException(status_code=status_code, detail=msg)
        return LogoutResponse(ok=True)

    # DISABLE MFA (con OTP)
    async def disable_mfa(
        self,
        payload: MfaDisableInput,
        creds: HTTPAuthorizationCredentials = Depends(bearer),
    ) -> VerifyMfaResponse:
        access_token = creds.credentials
        user_res = await supabase_service.get_user_from_access_token(access_token)
        if user_res.get("error"):
            raise HTTPException(status_code=401, detail="Token non valido o scaduto.")

        factors = user_res.get("factors", [])
        totp_factor = next((f for f in factors if f.get("factor_type") == "totp" and f.get("status") == "verified"), None)
        if not totp_factor:
            raise HTTPException(status_code=404, detail="Nessun fattore MFA di tipo TOTP attivo trovato.")

        factor_id = totp_factor.get("id")
        challenge_res = await supabase_service.create_mfa_challenge(access_token, factor_id)
        challenge_id = challenge_res.get("id")
        if not challenge_id:
             raise HTTPException(status_code=500, detail="Impossibile creare la challenge MFA per la verifica.")

        verify_res = await supabase_service.verify_mfa_challenge(access_token, factor_id, challenge_id, payload.code)
        if verify_res.get("error"):
            raise HTTPException(status_code=401, detail="Codice OTP non valido.")

        aal2_token = verify_res.get("access_token")
        if not aal2_token:
            raise HTTPException(status_code=500, detail="Verifica riuscita ma token AAL2 mancante.")

        delete_res = await supabase_service.delete_mfa_factor(aal2_token, factor_id)
        if delete_res.get("error"):
            raise HTTPException(status_code=500, detail="Errore durante l'eliminazione del fattore MFA.")

        refreshed_user_res = await supabase_service.get_user_from_access_token(aal2_token)
        if refreshed_user_res.get("error"):
            raise HTTPException(status_code=500, detail="Impossibile recuperare lo stato utente aggiornato.")

        return VerifyMfaResponse(
            access_token=aal2_token,
            token_type=verify_res.get("token_type", "bearer"),
            expires_in=verify_res.get("expires_in"),
            refresh_token=verify_res.get("refresh_token"),
            user=refreshed_user_res,
        )

    # REGISTER
    async def register(
        self,
        payload: RegisterInput,
        db: AsyncSession = Depends(get_db),
    ) -> RegisterResponse:
        # Prepara i metadati utente, includendo il nome.
        # Se user_meta è già presente, lo aggiorniamo, altrimenti lo creiamo.
        user_meta = payload.user_meta or {}
        user_meta['display_name'] = payload.name

        res = await supabase_service.register_user(
            email=payload.email,
            password=payload.password,
            user_meta=user_meta,
            app_meta=payload.app_meta,
            phone=payload.phone,
        )

        # ---- DEBUG REGISTRATION ----
        print("--- DEBUG REGISTER RESPONSE ---")
        print(f"Response from Supabase: {res}")
        print("-----------------------------")
        # --------------------------

        if res.get("error"):
            msg = res.get("message") or "Registrazione fallita"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

        user = (res.get("user") or {})
        user_id_str = user.get("id")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Registrazione completata ma user.id mancante",
            )

        # Assegna il ruolo 'user' predefinito al nuovo utente.
        # L'ID del ruolo 'user' è statico e definito dal sistema.
        user_role_id = UUID("0cc83a82-88f8-4ed9-9c92-ec9e09b266fd")
        repo = UserRoleRepository(db)
        try:
            await repo.assign(user_id=UUID(user_id_str), role_id=user_role_id)
        except IntegrityError:
            # L'utente potrebbe già avere il ruolo, ignoriamo l'errore.
            pass

        return RegisterResponse(user_id=user_id_str, email=user.get("email"), user=user)

    # LOGOUT
    async def logout(
        self,
        claims=Depends(get_current_claims),
    ) -> LogoutResponse:
        user_id = claims.get("sub")
        if user_id:
            res = await supabase_service.admin_logout_user(user_id)
            if res.get("error"):
                http_status = int(res.get("http_status") or 500)
                if http_status >= 500:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"Logout admin error {http_status}: {res.get('message')}",
                    )
        return LogoutResponse(ok=True)