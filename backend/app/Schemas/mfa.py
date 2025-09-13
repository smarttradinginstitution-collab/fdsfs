# app/Schemas/mfa.py

from pydantic import BaseModel, Field
from uuid import UUID

class MfaVerifyRequest(BaseModel):
    factor_id: UUID
    code: str = Field(..., min_length=6, max_length=6, description="Codice TOTP a 6 cifre")
