from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable, Awaitable

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"

        # Updated CSP to allow Swagger UI to load its resources from the CDN.
        # 'unsafe-inline' is required for Swagger's inline scripts.
        csp = (
            "default-src 'self';"
            " script-src 'self' 'unsafe-inline' cdn.jsdelivr.net;"
            " style-src 'self' 'unsafe-inline' cdn.jsdelivr.net;"
            " img-src 'self' data: https://fastapi.tiangolo.com;"
            " object-src 'none';"
        )
        response.headers["Content-Security-Policy"] = csp

        return response
