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
        print(f"--- REQUEST START --- {request.method} {request.url.path}")

        response = await call_next(request)

        end_time = time.time()
        duration = end_time - start_time
        print(f"--- REQUEST END --- Duration: {duration:.4f}s")

        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        #response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; object-src 'none';"
        return response
