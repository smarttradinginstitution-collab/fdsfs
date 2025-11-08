# backend/app/celery_app.py
import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# Recupera la configurazione del broker dall'ambiente, con un default per lo sviluppo locale con RabbitMQ
BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")
# Per RabbitMQ, il backend dei risultati è spesso gestito diversamente o non è necessario se lo stato è nel DB.
# Usiamo rpc:// che invia gli stati indietro tramite canali AMQP.
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "rpc://")

# Inizializza l'applicazione Celery
celery_app = Celery(
    "worker",  # Nome del worker
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    include=["app.tasks"]  # Specifica dove trovare i task
)

# Configurazione opzionale per instradare task specifici a code specifiche
celery_app.conf.task_routes = {
    "app.tasks.process_import_task": {"queue": "imports"},
}

celery_app.conf.update(
    task_track_started=True,
)
