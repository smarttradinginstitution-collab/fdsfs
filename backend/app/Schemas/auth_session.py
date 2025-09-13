# app/Schemas/auth_session.py

from __future__ import annotations
from typing import Any, Dict, Optional
from pydantic import BaseModel, EmailStr, Field

# ───────────── Ingressi ─────────────

class LoginInput(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)

class RegisterInput(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    user_meta: Optional[Dict[str, Any]] = None
    app_meta: Optional[Dict[str, Any]] = None
    phone: Optional[str] = None

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
