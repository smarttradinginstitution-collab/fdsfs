# app/main.py
import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.Router.routes import router
from app.config import settings
from app.Middleware.security_headers import SecurityHeadersMiddleware

# Custom key function to exclude OPTIONS requests from rate limiting
def key_func_excluding_options(request: Request) -> str:
    if request.method == "OPTIONS":
        return None
    return get_remote_address(request)

limiter = Limiter(key_func=key_func_excluding_options)
app = FastAPI(title=settings.APP_NAME)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# --- Static Files Mounting ---
# This makes the 'static' directory available so uploaded images can be served.
# os.makedirs("static", exist_ok=True)
# app.mount("/static", StaticFiles(directory="static"), name="static")


app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/", tags=["health"])
@limiter.limit("5/minute")
async def health(request: Request):
    return {"status": "ok"}

app.include_router(router)