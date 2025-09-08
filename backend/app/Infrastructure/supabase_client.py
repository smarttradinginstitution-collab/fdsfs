# app/Infrastructure/supabase_client.py
from __future__ import annotations

from functools import lru_cache
from supabase import create_client, Client  # pip install supabase

from app.config import settings


@lru_cache(maxsize=1)
def get_supabase() -> Client:
    """
    Client Supabase condiviso (thread-safe per l'uso tipico).
    Usa SUPABASE_PROJECT_URL e SUPABASE_KEY dal tuo settings.
    """
    url = settings.SUPABASE_PROJECT_URL
    key = settings.SUPABASE_KEY
    if not url or not key:
        raise RuntimeError("SUPABASE_PROJECT_URL / SUPABASE_KEY non configurati")
    return create_client(url, key)
