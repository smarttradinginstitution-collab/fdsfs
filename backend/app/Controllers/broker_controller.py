# app/Controllers/broker_controller.py
from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends

from app.Services.broker_service import BrokerService
from app.Schemas.broker import BrokerRead

router = APIRouter(
    prefix="/brokers",
    tags=["Brokers"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[BrokerRead])
async def get_all_brokers(
    service: BrokerService = Depends(),
):
    """
    Retrieves a list of all available brokers.
    """
    return await service.get_all_brokers()