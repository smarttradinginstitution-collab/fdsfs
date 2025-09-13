# backend/app/Middleware/security_headers.py
import secrets
from typing import Callable, Awaitable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        # Genera nonce univoco per ogni richiesta
        csp_nonce = secrets.token_hex(16)
        request.state.csp_nonce = csp_nonce

        response = await call_next(request)

        # --- Content Security Policy minima e restrittiva ---
        csp = (
            "default-src 'self'; "
            "base-uri 'self'; "
            "object-src 'none'; "
            f"style-src 'self' 'nonce-{csp_nonce}'; "
            f"script-src 'self' 'nonce-{csp_nonce}'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "frame-src 'self'; "
            "connect-src 'self'; "
            "form-action 'self'; "
            "upgrade-insecure-requests"
        )
        response.headers["Content-Security-Policy"] = csp

        # --- Altri header di sicurezza ---
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer-when-downgrade"

        # HSTS solo se in HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response
