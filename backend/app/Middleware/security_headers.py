from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable, Awaitable

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        import time
        start_time = time.time()
        print(f"SECURITY_MIDDLEWARE: Start at {start_time:.4f}")

        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        #response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; object-src 'none';"

        end_time = time.time()
        print(f"SECURITY_MIDDLEWARE: End at {end_time:.4f}. Duration: {end_time - start_time:.4f}s")

        return response
