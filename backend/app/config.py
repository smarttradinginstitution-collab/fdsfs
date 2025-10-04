# app/config.py
from typing import Optional, List
from urllib.parse import quote_plus
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "My FastAPI App"
    ENV: str = "dev"

    # Trattiamo CORS_ORIGINS come stringa "semplice" per evitare json.loads automatico di Pydantic
    # Esempi validi in .env:
    #   CORS_ORIGINS=http://localhost:5173
    #   CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
    CORS_ORIGINS: Optional[str] = Field(default="http://localhost:5173")

    DB_SSL_VERIFY: bool = True

    DATABASE_URL: Optional[str] = Field(default=None)
    DB_HOST: Optional[str] = None
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASS: Optional[str] = None
    DB_PORT: Optional[int] = 5432
    DB_CHARSET: Optional[str] = "utf8"

    SUPABASE_PROJECT_URL: str
    SUPABASE_KEY: str
    AUTH_AUTO_CONFIRM_DEV: bool = True

    def assemble_db_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        if not (self.DB_HOST and self.DB_NAME and self.DB_USER and self.DB_PASS):
            raise ValueError("Devi impostare DATABASE_URL oppure tutte le variabili DB_*")
        user = self.DB_USER
        from urllib.parse import quote_plus
        pwd = quote_plus(self.DB_PASS)
        return f"postgresql+asyncpg://{user}:{pwd}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def cors_origins_list(self) -> List[str]:
        """
        Converte la stringa CORS_ORIGINS in una lista e aggiunge origini di sviluppo comuni.
        """
        # Set di base per lo sviluppo, per garantire che funzioni localmente
        # a prescindere dal file .env
        # Set di base per lo sviluppo, per garantire che funzioni localmente
        # a prescindere dal file .env. Aggiungiamo più porte comuni per Vite.
        origins = {
            "http://localhost:5173",
            "http://localhost:5174",
            "http://localhost:5175",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
            "http://127.0.0.1:5175",
        }

        # Per lo sviluppo, è spesso utile permettere tutte le origini.
        # In produzione, questa logica dovrebbe essere più restrittiva.
        if self.ENV == "dev":
            origins.add("*")

        if self.CORS_ORIGINS:
            # Aggiunge le origini definite nell'ambiente
            custom_origins = {x.strip() for x in self.CORS_ORIGINS.split(",") if x.strip()}
            origins.update(custom_origins)

        return list(origins)

settings = Settings()
settings.DATABASE_URL = settings.assemble_db_url()
