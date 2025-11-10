# backend/app/celery_app.py
import os
from celery import Celery

# Carica le variabili d'ambiente, con valori di default per lo sviluppo locale
BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery(
    "trading_imports",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    include=["app.tasks"]  # Specifica dove trovare i task
)

# Invia i task di importazione a una coda dedicata chiamata "imports"
# Questo permette di avere worker specializzati per questo tipo di lavoro.
celery_app.conf.task_routes = {
    "app.tasks.process_import_task": {"queue": "imports"},
}

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
