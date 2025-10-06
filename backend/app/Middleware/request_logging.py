# app/Middleware/request_logging.py
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable, Awaitable

from app.Infrastructure.db import SessionLocal
from app.Models.request_log import RequestLog

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Escludi i percorsi relativi al monitoraggio stesso
        if request.url.path.startswith("/api/v1/request-logs"):
            return await call_next(request)

        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time
        response_time_ms = int(process_time * 1000)

        # Crea un nuovo record di log
        log_entry = RequestLog(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            response_time_ms=response_time_ms,
        )

        # Salva nel database in modo asincrono
        try:
            async with SessionLocal() as session:
                session.add(log_entry)
                await session.commit()
        except Exception as e:
            # In caso di errore nel logging, non bloccare la risposta principale.
            # Potresti voler loggare l'errore `e` con un logger standard.
            print(f"Error logging request: {e}")

        return response