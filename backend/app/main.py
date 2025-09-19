# app/main.py
# This file is the main entry point for the FastAPI application.
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.Router.routes import router
from app.config import settings
from app.Middleware.security_headers import SecurityHeadersMiddleware

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title=settings.APP_NAME)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


app.add_middleware(SecurityHeadersMiddleware)
# Add the backend's own origins for docs and local development
# This is useful for accessing the docs and for tools like Postman
dev_origins = settings.cors_origins_list
if settings.ENV == "dev":
    dev_origins.extend([
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=dev_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["health"])
@limiter.limit("5/minute")
async def health(request: Request):
    return {"status": "ok"}

app.include_router(router)
