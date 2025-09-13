# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.Router.routes import router
from app.config import settings
from app.Middleware.security_headers import SecurityHeadersMiddleware

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["health"])
async def health():
    return {"status": "ok"}

app.include_router(router)
