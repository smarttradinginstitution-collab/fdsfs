from __future__ import annotations
from supabase import create_client, Client
from app.config import settings

# Type alias for clarity in dependency injection
SupabaseClient = Client

def get_supabase_client() -> SupabaseClient:
    """
    Dependency function to create and yield a Supabase client.
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
        raise ValueError("Supabase URL and Service Key must be set in environment variables.")

    supabase: SupabaseClient = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_KEY
    )
    return supabase