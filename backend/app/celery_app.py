# backend/app/celery_app.py
import os
from celery import Celery

# --- NUOVA LOGICA per usare il DB come Result Backend ---
# Recupera l'URL del database dalle variabili d'ambiente
DATABASE_URL = os.getenv("DATABASE_URL")
# Costruisce l'URL per il result backend di Celery (deve iniziare con 'db+')
# Esempio: "postgresql://..." diventa "db+postgresql://..."
RESULT_BACKEND_DB = f"db+{DATABASE_URL}" if DATABASE_URL else None

# --- Configurazione Principale ---
BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")
# Usa il database come result backend. Se l'URL del DB non è disponibile,
# usa 'rpc://' come fallback (che non richiede dipendenze esterne).
RESULT_BACKEND = RESULT_BACKEND_DB or "rpc://"


celery_app = Celery(
    "trading_imports",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    include=["app.tasks"]  # Specifica dove trovare i task
)

# Invia i task di importazione a una coda dedicata chiamata "imports"
celery_app.conf.task_routes = {
    "app.tasks.process_import_task": {"queue": "imports"},
}

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Aggiunta configurazione per il backend DB
    result_extended=True
)
