# backend/app/Router/soa_router.py
from fastapi import APIRouter
from app.Controllers import soa_controller

"""
This router handles all endpoints related to Strength & Opportunity Analysis (SOA).

It includes the main analysis endpoint that provides a comprehensive, multi-level
evaluation of trading performance.
"""

router = APIRouter()

router.include_router(soa_controller.router)
