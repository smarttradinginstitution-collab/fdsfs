# backend/app/Router/soa_router.py
from fastapi import APIRouter
from app.Controllers import soa_controller

router = APIRouter()

router.include_router(soa_controller.router, prefix="/analytics", tags=["SOA Analytics"])
