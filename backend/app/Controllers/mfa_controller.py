# app/Controllers/mfa_controller.py
from __future__ import annotations

from typing import Dict
from uuid import UUID

from fastapi import Depends, HTTPException, status

from app.Infrastructure import supabase_service as supabase
from app.Router.auth import get_current_claims
from app.Schemas.mfa import MfaVerifyRequest

class MfaController:
    """Controller per la gestione del flusso MFA."""

    async def enroll(self, claims: Dict = Depends(get_current_claims)) -> Dict:
        """
        Inizia il processo di enrollment per un nuovo fattore MFA (TOTP)
        per l'utente autenticato.
        """
        user_id = claims.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="ID utente non trovato nel token.",
            )

        res = await supabase.admin_enroll_mfa(user_id)
        if res.get("error"):
            raise HTTPException(
                status_code=res.get("http_status", 500),
                detail=res.get("message") or "Errore durante l'enrollment MFA.",
            )

        # Estrai i dati necessari per il frontend
        factor_id = res.get("id")
        qr_code_svg = res.get("totp", {}).get("qr_code")

        if not factor_id or not qr_code_svg:
            raise HTTPException(
                status_code=500,
                detail="Risposta da Supabase incompleta per l'enrollment MFA.",
            )

        return {"factor_id": factor_id, "qr_code_svg": qr_code_svg}

    async def verify_enrollment(self, payload: MfaVerifyRequest, claims: Dict = Depends(get_current_claims)) -> Dict:
        """
        Verifica e finalizza l'enrollment di un fattore MFA.
        Questo endpoint viene chiamato dopo che l'utente ha scansionato il QR code
        e ha inserito il primo codice TOTP.
        """
        user_id = claims.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="ID utente non trovato nel token.",
            )

        res = await supabase.admin_verify_mfa(user_id, str(payload.factor_id), payload.code)
        if res.get("error"):
            raise HTTPException(
                status_code=res.get("http_status", 400),
                detail=res.get("message") or "Codice MFA non valido o errore durante la verifica.",
            )

        # Se la verifica ha successo, Supabase ritorna i dettagli del fattore.
        # Possiamo semplicemente ritornare un messaggio di successo.
        return {"status": "ok", "message": "Fattore MFA verificato e abilitato con successo."}
