# backend/app/celery_app.py
import os
from dotenv import load_dotenv
from celery import Celery

# Carica esplicitamente le variabili d'ambiente dal file .env
# Questo è cruciale per il worker che potrebbe non essere avviato
# dalla stessa directory o con lo stesso contesto di Pydantic.
load_dotenv()

# --- Configurazione Principale ---
BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND") or "rpc://"


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
