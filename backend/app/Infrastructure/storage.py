# backend/app/Infrastructure/storage.py
import os
from supabase import create_client, Client
from fastapi import UploadFile
import uuid

# Inizializza il client Supabase usando le variabili d'ambiente
# Queste credenziali danno al backend i permessi per agire come servizio (service_role)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_IMPORT_BUCKET", "imports")

# Crea un'istanza del client solo se le credenziali sono disponibili
supabase: Client | None = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def upload_import_file(upload_file: UploadFile, import_run_id: uuid.UUID) -> str:
    """
    Carica un file su Supabase Storage in modo asincrono.

    Args:
        upload_file: L'oggetto UploadFile di FastAPI.
        import_run_id: L'ID della run di importazione per creare un percorso univoco.

    Returns:
        Il percorso del file nello storage.

    Raises:
        ConnectionError: Se il client Supabase non è configurato.
        Exception: Per errori durante l'upload.
    """
    if not supabase:
        raise ConnectionError("Supabase client non è configurato. Controlla le variabili d'ambiente.")

    content = await upload_file.read()
    # Crea un percorso univoco per evitare collisioni di nomi
    storage_path = f"{import_run_id}/{upload_file.filename}"

    try:
        # L'SDK di Supabase per Python usa chiamate sincrone, quindi la eseguiamo
        # in questo modo. Per un'app ad alto traffico, si potrebbe eseguire
        # in un thread separato con `asyncio.to_thread`.
        supabase.storage.from_(SUPABASE_BUCKET).upload(
            path=storage_path,
            file=content,
            file_options={"content-type": upload_file.content_type or "application/octet-stream"}
        )
        return storage_path
    except Exception as e:
        # Logga l'errore e rilancia per gestirlo a un livello superiore
        print(f"Errore durante l'upload su Supabase Storage: {e}")
        raise

def download_import_file(path: str) -> bytes:
    """
    Scarica un file da Supabase Storage.

    Questa funzione è sincrona perché verrà eseguita all'interno di un worker Celery,
    che opera in un contesto sincrono.

    Args:
        path: Il percorso del file da scaricare.

    Returns:
        Il contenuto del file in bytes.

    Raises:
        ConnectionError: Se il client Supabase non è configurato.
        Exception: Per errori durante il download.
    """
    if not supabase:
        raise ConnectionError("Supabase client non è configurato. Controlla le variabili d'ambiente.")

    try:
        response = supabase.storage.from_(SUPABASE_BUCKET).download(path)
        return response
    except Exception as e:
        print(f"Errore durante il download da Supabase Storage: {e}")
        raise
