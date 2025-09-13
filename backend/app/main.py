# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.Router.routes import router
from app.config import settings

app = FastAPI(title=settings.APP_NAME)


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
# dove vuoi (es. in un router /healthz)
from fastapi import APIRouter
from app.Infrastructure.db import check_connection

router = APIRouter()
@router.get("/healthz/db")
async def healthz_db():
    ok = await check_connection()
    return {"db": "ok" if ok else "fail"}
app.include_router(router)
