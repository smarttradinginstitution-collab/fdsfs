# backend/app/Infrastructure/storage.py
import os
import uuid
from supabase import create_client, Client
from fastapi import UploadFile
from dotenv import load_dotenv

load_dotenv()

# Inizializza il client di Supabase usando le variabili d'ambiente
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_IMPORT_BUCKET", "imports")

# Crea un'istanza del client solo se le credenziali sono disponibili
supabase_client: Client | None = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def upload_import_file(upload_file: UploadFile, import_run_id: uuid.UUID) -> str:
    """
    Carica un file nello storage di Supabase e restituisce il percorso.

    Il percorso è strutturato come: {import_run_id}/{nome_file_originale}
    """
    if not supabase_client:
        raise ConnectionError("Supabase client non è inizializzato. Controlla le variabili d'ambiente.")

    content = await upload_file.read()
    # Costruisce un percorso univoco per evitare collisioni ma mantenendo il nome del file
    storage_path = f"{import_run_id}/{upload_file.filename}"

    try:
        # L'upload è un'operazione bloccante, ma la gestiamo qui
        supabase_client.storage.from_(SUPABASE_BUCKET).upload(
            path=storage_path,
            file=content,
            file_options={"content-type": upload_file.content_type or "application/octet-stream"}
        )
    except Exception as e:
        # Qui potresti loggare l'errore specifico restituito da Supabase
        raise IOError(f"Impossibile caricare il file su Supabase Storage: {e}") from e

    return storage_path

def download_import_file(path: str) -> bytes:
    """
    Scarica un file dallo storage di Supabase dato il suo percorso.
    Questa funzione è pensata per essere usata dai worker Celery.
    """
    if not supabase_client:
        raise ConnectionError("Supabase client non è inizializzato. Controlla le variabili d'ambiente.")

    try:
        # download() è un'operazione sincrona/bloccante
        response = supabase_client.storage.from_(SUPABASE_BUCKET).download(path)
        return response
    except Exception as e:
        raise FileNotFoundError(f"Impossibile scaricare il file da Supabase Storage al percorso {path}: {e}") from e
