# app/Infrastructure/supabase_service.py

from __future__ import annotations
import httpx
from typing import Any, Dict, Optional
from datetime import datetime, timezone

from app.config import settings

"""
Service async per Supabase Auth (GoTrue).
TUTTE le chiamate usano la SERVICE KEY nel solo header 'apikey'.
Per ottenere l'utente corrente da un access token del client, chiamiamo
/auth/v1/user con:
  - Authorization: Bearer <access_token>
  - apikey: <SUPABASE_KEY>
"""

def _service_headers() -> dict[str, str]:
    k = settings.SUPABASE_SERVICE_KEY
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "apikey": k,  # obbligatorio per Supabase
    }

async def _request(
    method: str,
    path: str,
    json: Optional[dict] = None,
    extra_headers: Optional[dict[str, str]] = None,
) -> Dict[str, Any]:
    base = settings.SUPABASE_URL.rstrip("/")
    url = f"{base}{path}"
    timeout = httpx.Timeout(30.0, connect=8.0)
    headers = _service_headers()
    if extra_headers:
        headers.update(extra_headers)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.request(method, url, headers=headers, json=json)

    try:
        data: Dict[str, Any] = resp.json() if resp.content else {}
    except Exception:
        data = {"message": "Invalid JSON response from Supabase"}

    if resp.status_code >= 400:
        return {
            "error": "auth",
            "message": data.get("msg")
            or data.get("error_description")
            or data.get("message")
            or "error",
            "http_status": resp.status_code,
            "error_code": data.get("error") or "ERROR",
            "raw": data,
        }

    data["http_status"] = resp.status_code
    data["error"] = None
    return data


# ----------------- Flussi "user" (ok solo apikey) -----------------

async def sign_up(email: str, password: str, user_meta: Optional[dict] = None) -> Dict[str, Any]:
    payload = {"email": email, "password": password}
    if user_meta:
        payload["data"] = user_meta
    return await _request("POST", "/auth/v1/signup", payload)

async def sign_in(email: str, password: str) -> Dict[str, Any]:
    payload = {"email": email, "password": password}
    return await _request("POST", "/auth/v1/token?grant_type=password", payload)


# ----------------- Flussi "admin" (SERVE Authorization Bearer service_role) -----------------

def _admin_auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}"}

async def update_user(user_id: str, patch: dict) -> Dict[str, Any]:
    return await _request(
        "PUT",
        f"/auth/v1/admin/users/{user_id}",
        patch,
        extra_headers=_admin_auth_headers(),
    )

async def admin_logout_user(user_id: str) -> Dict[str, Any]:
    return await _request(
        "POST",
        f"/auth/v1/admin/users/{user_id}/logout",
        json={},
        extra_headers=_admin_auth_headers(),
    )

async def admin_confirm_user(user_id: str) -> Dict[str, Any]:
    now_iso = datetime.now(timezone.utc).isoformat()
    patch = {"email_confirmed_at": now_iso}
    return await update_user(user_id, patch)


async def register_user(
    email: str,
    password: str,
    user_meta: Optional[dict] = None,
    app_meta: Optional[dict] = None,
    banned_until: Optional[str] = None,
    phone: Optional[str] = None,
) -> Dict[str, Any]:
    res = await sign_up(email, password, user_meta or {})
    if res.get("error"):
        return res

    user = (res.get("user") or {})
    user_id = user.get("id")
    if not user_id:
        return res

    patch: dict = {}
    if app_meta is not None:
        patch["app_metadata"] = app_meta
    if banned_until is not None:
        patch["banned_until"] = banned_until
    if phone is not None:
        patch["phone"] = phone

    if patch:
        upd = await update_user(user_id, patch)
        if not upd.get("error") and isinstance(upd.get("user"), dict):
            res["user"] = upd["user"]

    if settings.ENV == "dev" and settings.AUTH_AUTO_CONFIRM_DEV:
        conf = await admin_confirm_user(user_id)
        if not conf.get("error") and isinstance(conf.get("user"), dict):
            res["user"] = conf["user"]

    return res


# ----------------- Utente corrente da access token (client) -----------------

async def get_user_from_access_token(access_token: str) -> Dict[str, Any]:
    """
    /auth/v1/user:
      - Authorization: Bearer <access_token>
      - apikey: <SUPABASE_KEY>
    """
    if not access_token:
        return {"error": "auth", "message": "missing token", "http_status": 401}
    return await _request(
        "GET",
        "/auth/v1/user",
        json=None,
        extra_headers=_bearer_auth_headers(access_token),
    )

# ----------------- Flussi MFA (richiedono Bearer token utente) -----------------

def _bearer_auth_headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}

async def enroll_totp(access_token: str, friendly_name: Optional[str] = None) -> Dict[str, Any]:
    """Inizia l'enroll di un fattore TOTP."""
    payload = {"factor_type": "totp"}
    if friendly_name:
        payload["friendly_name"] = friendly_name
    return await _request(
        "POST",
        "/auth/v1/factors",
        json=payload,
        extra_headers=_bearer_auth_headers(access_token),
    )

async def create_mfa_challenge(access_token: str, factor_id: str) -> Dict[str, Any]:
    """Crea una challenge per un fattore MFA. Necessario per l'enroll e la verifica."""
    return await _request(
        "POST",
        f"/auth/v1/factors/{factor_id}/challenge",
        json={},
        extra_headers=_bearer_auth_headers(access_token),
    )

async def verify_mfa_challenge(
    access_token: str, factor_id: str, challenge_id: str, code: str
) -> Dict[str, Any]:
    """Verifica una challenge MFA con un codice OTP."""
    payload = {"challenge_id": challenge_id, "code": code}
    return await _request(
        "POST",
        f"/auth/v1/factors/{factor_id}/verify",
        json=payload,
        extra_headers=_bearer_auth_headers(access_token),
    )

async def list_factors(access_token: str) -> Dict[str, Any]:
    """Elenca i fattori MFA dell'utente. Ritorna l'oggetto User completo."""
    # L'oggetto utente contiene già i fattori, quindi riutilizziamo la funzione esistente.
    return await get_user_from_access_token(access_token)

async def delete_mfa_factor(access_token: str, factor_id: str) -> Dict[str, Any]:
    """Elimina un fattore MFA per un utente."""
    return await _request(
        "DELETE",
        f"/auth/v1/factors/{factor_id}",
        extra_headers=_bearer_auth_headers(access_token),
    )
