# app/config.py
from __future__ import annotations

from pathlib import Path
from typing import Optional, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- App ---
    APP_NAME: str = "My FastAPI App"
    ENV: str = Field(default="prod")
    # stringa separata da virgole nell'env
    CORS_ORIGINS: str = ""

    # --- DB ---
    DATABASE_URL: str

    DB_SSL_VERIFY: bool = Field(default=True)
    # system | certifi | custom | merge | system+custom
    DB_SSL_CA_MODE: Literal["system", "certifi", "custom", "merge", "system+custom"] = Field(
        default="merge"
    )
    SSL_CERT_FILE: Optional[str] = None  # relativo alla root backend o assoluto

    # --- Supabase ---
    SUPABASE_PROJECT_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    AUTH_AUTO_CONFIRM_DEV: bool = Field(default=False)

    @property
    def cors_origins_list(self) -> list[str]:
        raw = self.CORS_ORIGINS or ""
        return [s.strip() for s in raw.split(",") if s.strip()]

    def resolve_path(self, p: Optional[str]) -> Optional[Path]:
        if not p:
            return None
        path = Path(p)
        base = BACKEND_DIR
        return path if path.is_absolute() else (base / path)

    @field_validator("ENV", mode="before")
    @classmethod
    def _norm_env(cls, v: str) -> str:
        return (v or "").strip().lower() or "prod"


settings = Settings()
