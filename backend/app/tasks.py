# backend/app/tasks.py
import asyncio
import uuid
from typing import List
from app.celery_app import celery_app
from app.Infrastructure.db import SessionLocal
from app.Infrastructure.storage import download_import_file
from app.Services.import_service import ImportService


@celery_app.task(name="app.tasks.process_import_task")
def process_import_task(import_run_id: str, storage_paths: List[str], platform: str):
    """
    Task Celery eseguito in background da un worker.

    Questo task orchestra l'intero processo di importazione:
    1. Crea una sessione di database indipendente.
    2. Scarica i file necessari da Supabase Storage.
    3. Invoca il servizio di importazione per processare i dati.
    4. Gestisce gli errori, assicurando che lo stato della ImportRun sia sempre aggiornato.
    """
    asyncio.run(_process_import_async(import_run_id, storage_paths, platform))


async def _process_import_async(import_run_id_str: str, storage_paths: List[str], platform: str):
    """
    Funzione ausiliaria asincrona che contiene la logica effettiva del task.
    """
    import_run_id = uuid.UUID(import_run_id_str)

    # 1. Crea una sessione di database dedicata per questo task
    async with SessionLocal() as session:
        service = ImportService(session)
        import_run = await service.get_import_run(import_run_id)

        if not import_run:
            # Se la run non esiste, non c'è nulla da fare. Loggare l'errore.
            print(f"ERRORE CRITICO: Impossibile trovare la ImportRun con ID {import_run_id} nel task Celery.")
            return

        try:
            # Recupera i contenuti di tutti i file prima di iniziare l'elaborazione
            file_contents = [download_import_file(path) for path in storage_paths]

            # 2. Invoca il metodo di servizio corretto in base alla piattaforma
            if platform.lower() == "tradovate":
                # Per Tradovate, passiamo la lista di contenuti
                await service.process_tradovate_import(import_run_id, file_contents)
            elif platform.lower() == "mt5":
                # Per MT5, ci aspettiamo un solo file
                if len(file_contents) != 1:
                    raise ValueError(f"MT5 si aspetta 1 file, ma ne sono stati forniti {len(file_contents)}")
                await service.process_mt5_import(import_run_id, file_contents[0])
            else:
                raise ValueError(f"Piattaforma sconosciuta: {platform}")

        except Exception as e:
            # 3. Gestione centralizzata degli errori
            # Se qualsiasi cosa va storta, aggiorniamo la run a 'failed'
            error_message = f"Errore durante l'esecuzione del task di importazione: {type(e).__name__}: {e}"
            print(error_message) # Logga l'errore per il debug

            # Assicurati che la sessione sia ancora valida per l'aggiornamento
            if not session.is_active:
                session = SessionLocal()
                service = ImportService(session)

            await service.update_import_run_status(
                import_run_id=import_run_id,
                new_status="failed",
                error_message=error_message
            )
            await session.commit()
