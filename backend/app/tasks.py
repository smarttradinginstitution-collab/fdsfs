# backend/app/tasks.py
import asyncio
import uuid
from app.celery_app import celery_app
from app.Infrastructure.db import SessionLocal as async_session_maker # CORREZIONE: Importa con il nome corretto
from app.Infrastructure.storage import download_import_file
from app.Services.import_service import ImportService

@celery_app.task(name="app.tasks.process_import_task", bind=True, max_retries=3)
def process_import_task(self, import_run_id_str: str, storage_path: str, platform: str):
    """
    Task Celery eseguito dal worker per processare un file di importazione.

    Questa funzione è il wrapper sincrono che Celery invoca.
    Al suo interno, avvia il loop di eventi asyncio per eseguire la logica asincrona.

    Args:
        self: L'istanza del task, per gestire retry, etc.
        import_run_id_str: L'ID della run di importazione (come stringa).
        storage_path: Il percorso del file in Supabase Storage.
        platform: La piattaforma di origine (es. "mt5", "tradovate", "ninjatrader").
    """
    try:
        # Esegue la funzione asincrona principale e attende il suo completamento
        asyncio.run(_process_import_async(import_run_id_str, storage_path, platform))
    except Exception as exc:
        # In caso di errore imprevisto, logga l'errore e ritenta il task
        print(f"Errore durante l'esecuzione del task per l'import {import_run_id_str}: {exc}")
        # `self.retry` solleverà un'eccezione per far ritentare a Celery,
        # con un backoff esponenziale.
        raise self.retry(exc=exc, countdown=60) # Riprova tra 60 secondi


async def _process_import_async(import_run_id_str: str, storage_path: str, platform: str):
    """
    Logica asincrona per l'elaborazione del file.
    """
    import_run_id = uuid.UUID(import_run_id_str)

    # 1. Crea una nuova sessione di database per questo task.
    #    Questo garantisce l'isolamento e previene problemi di sessioni condivise.
    async with async_session_maker() as session:
        service = ImportService(session)

        try:
            # 2. Scarica il file da Supabase Storage.
            #    Questa è una chiamata bloccante, quindi ideale per un worker.
            file_content = download_import_file(storage_path)

            # 3. Seleziona e avvia il processo di importazione corretto
            #    in base alla piattaforma.
            platform_key = platform.lower()
            if platform_key == "tradovate":
                await service.process_tradovate_import(import_run_id, file_content)
            elif platform_key == "mt5":
                await service.process_mt5_import(import_run_id, file_content)
            elif platform_key == "ninjatrader":
                await service.process_ninjatrader_import(import_run_id, file_content)
            else:
                # Se la piattaforma non è supportata, aggiorna la run con un errore.
                import_run = await service.get_import_run(import_run_id)
                if import_run:
                    import_run.status = "failed"
                    import_run.error_message = f"Piattaforma non supportata: {platform}"
                    await session.commit()
                raise ValueError(f"Piattaforma non supportata: {platform}")

        except Exception as e:
            # In caso di errore durante l'elaborazione, marca la run come 'failed'
            # e registra il messaggio di errore nel database.
            print(f"Fallimento nel processare l'import {import_run_id}: {e}")
            import_run = await service.get_import_run(import_run_id)
            if import_run:
                import_run.status = "failed"
                import_run.error_message = str(e)
                await session.commit()
            # Rilancia l'eccezione per farla gestire al wrapper sincrono (che farà il retry).
            raise
