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
        # Il valore 'aal' è nel token, non nell'oggetto user. Lo estraiamo.
        aal = None
        try:
            decoded_token = jwt.get_unverified_claims(access_token)
            aal = decoded_token.get("aal")
        except Exception:
            # Se la decodifica fallisce, non possiamo procedere con la logica MFA.
            # L'utente riceverà un token AAL1 standard, che è un fallback sicuro.
            pass

        # I 'factors' sono nell'oggetto user, che è corretto.
        factors = user_obj.get("factors")

        if aal == "aal1" and factors and len(factors) > 0:
            # L'utente ha MFA, dobbiamo avviare la challenge
            # Troviamo il primo fattore TOTP valido
            totp_factor = next((f for f in factors if f.get("factor_type") == "totp" and f.get("status") == "verified"), None)

            if totp_factor and access_token:
                factor_id = totp_factor.get("id")
                chal = await supabase_service.create_mfa_challenge(access_token, factor_id)
                challenge_id = chal.get("id")

                if challenge_id:
                    return LoginMfaChallenge(
                        status="mfa_required",
                        access_token=access_token,
                        factor_id=factor_id,
                        challenge_id=challenge_id,
                    )

        # Se non è richiesta MFA o se qualcosa è andato storto nella creazione della challenge,
        # ritorna il token AAL1 standard.
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
            # risposta non valida / codice errato
            raise HTTPException(status_code=401, detail=res.get("message") or "Codice OTP non valido")

        # Se la verifica ha successo, Supabase ritorna una nuova sessione AAL2.
        # Non è necessario nessun workaround con app_metadata.
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
        friendly = payload.friendly_name if payload else "Authenticator"

        res = await supabase_service.enroll_totp(access_token, friendly_name=friendly)
        if res.get("error"):
            msg = res.get("message") or "Enroll TOTP non riuscito"
            raise HTTPException(status_code=400, detail=msg)

        factor_id = res.get("id")
        if not factor_id:
            raise HTTPException(status_code=502, detail="Enroll riuscito ma senza factor_id")

        totp = res.get("totp") or {}
        # crea subito la challenge, così hai challenge_id da usare con l’OTP
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
    ) -> VerifyMfaResponse: # Ritorna una sessione aggiornata
        access_token = creds.credentials

        # 1. Trova il fattore TOTP attivo dell'utente
        user_res = await supabase_service.get_user_from_access_token(access_token)
        if user_res.get("error"):
            raise HTTPException(status_code=401, detail="Token non valido o scaduto.")

        factors = user_res.get("factors", [])
        totp_factor = next((f for f in factors if f.get("factor_type") == "totp" and f.get("status") == "verified"), None)
        if not totp_factor:
            raise HTTPException(status_code=404, detail="Nessun fattore MFA di tipo TOTP attivo trovato.")

        factor_id = totp_factor.get("id")

        # 2. Crea una challenge per il fattore
        challenge_res = await supabase_service.create_mfa_challenge(access_token, factor_id)
        challenge_id = challenge_res.get("id")
        if not challenge_id:
             raise HTTPException(status_code=500, detail="Impossibile creare la challenge MFA per la verifica.")

        # 3. Verifica il codice OTP per ottenere un token AAL2
        verify_res = await supabase_service.verify_mfa_challenge(access_token, factor_id, challenge_id, payload.code)
        if verify_res.get("error"):
            raise HTTPException(status_code=401, detail="Codice OTP non valido.")

        # 4. Usa il nuovo token AAL2 per eliminare il fattore
        aal2_token = verify_res.get("access_token")
        if not aal2_token:
            raise HTTPException(status_code=500, detail="Verifica riuscita ma token AAL2 mancante.")

        delete_res = await supabase_service.delete_mfa_factor(aal2_token, factor_id)
        if delete_res.get("error"):
            raise HTTPException(status_code=500, detail="Errore durante l'eliminazione del fattore MFA.")

        # 5. Ritorna la nuova sessione AAL2. L'oggetto utente in verify_res è già aggiornato.
        return VerifyMfaResponse(
            access_token=verify_res.get("access_token"),
            token_type=verify_res.get("token_type"),
            expires_in=verify_res.get("expires_in"),
            refresh_token=verify_res.get("refresh_token"),
            user=verify_res.get("user") or {},
        )

    # REGISTER
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
                detail="Registrazione completata ma user.id mancante",
            )

        stmt = select(Role.id).where(Role.name.ilike("user")).limit(1)
        role_id_row = await db.execute(stmt)
        role_id = role_id_row.scalar_one_or_none()
        if role_id:
            repo = UserRoleRepository(db)
            try:
                await repo.assign(user_id=UUID(user_id_str), role_id=role_id)
            except IntegrityError:
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
                # Gestisce solo errori critici (es. 5xx, auth errata), non 4xx (utente non trovato etc)
                http_status = int(res.get("http_status") or 500)
                if http_status >= 500:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"Logout admin error {http_status}: {res.get('message')}",
                    )
        return LogoutResponse(ok=True)
