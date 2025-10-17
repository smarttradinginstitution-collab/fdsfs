# app/Schemas/auth_session.py

from __future__ import annotations
from typing import Any, Dict, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

# ───────────── Ingressi ─────────────

class LoginInput(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)

class RegisterInput(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)
    user_meta: Optional[Dict[str, Any]] = None
    app_meta: Optional[Dict[str, Any]] = None
    phone: Optional[str] = None

    @field_validator('confirm_password')
    def passwords_match(cls, v: str, values: Dict[str, Any]) -> str:
        if 'password' in values.data and v != values.data['password']:
            raise ValueError('Le password non corrispondono')
        return v

# ───────────── Uscite ─────────────

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    user: Dict[str, Any]

class RegisterResponse(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    user: Dict[str, Any]
    status: str = "registered"

class LogoutResponse(BaseModel):
    ok: bool = True

# ───────────── MFA ─────────────

class LoginMfaChallenge(BaseModel):
    status: str = "mfa_required"
    access_token: str # Il token AAL1 da usare per la verifica
    factor_id: str
    challenge_id: str

class VerifyMfaInput(BaseModel):
    access_token: str
    factor_id: str
    challenge_id: str
    code: str = Field(..., description="Codice OTP (One-Time Password)")

class VerifyMfaResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    user: Dict[str, Any]

class TotpEnrollInput(BaseModel):
    friendly_name: Optional[str] = Field(None, description="Nome amichevole per il fattore MFA, es. 'Mio Telefono'")

class TotpEnrollResponse(BaseModel):
    factor_id: str
    secret: str
    otpauth_uri: str
    qr_code: str # SVG string
    challenge_id: str

class ListFactorsResponse(BaseModel):
    factors: list[Dict[str, Any]]

class MfaDisableInput(BaseModel):
    code: str = Field(..., description="Codice OTP (One-Time Password) per confermare la disattivazione")
