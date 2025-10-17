# backend/app/Router/journal_router.py
from __future__ import annotations

from datetime import date
from uuid import UUID
from fastapi import APIRouter, Depends, Body

from app.Controllers.journal_controller import JournalController
from app.Services.journal_service import JournalService
from app.Schemas.journal import JournalDay
from app.Schemas.daily_rule_instance import DailyRuleInstanceRead
from app.Router.auth import get_current_claims

router = APIRouter(
    prefix="/journal",
    tags=["Journal"],
    dependencies=[Depends(get_current_claims)],
)

journal_controller = JournalController()


@router.post("/start-day", response_model=JournalDay)
async def start_day(
    day: date = Body(..., embed=True),
    claims: dict = Depends(get_current_claims),
    service: JournalService = Depends(),
):
    return await journal_controller.start_day(claims, day, service)


@router.get("/day/{day}", response_model=JournalDay)
async def get_day(
    day: date,
    claims: dict = Depends(get_current_claims),
    service: JournalService = Depends(),
):
    return await journal_controller.get_day(claims, day, service)


@router.put("/rules/{instance_id}", response_model=DailyRuleInstanceRead)
async def update_manual_rule(
    instance_id: UUID,
    status: str = Body(..., embed=True),
    claims: dict = Depends(get_current_claims),
    service: JournalService = Depends(),
):
    return await journal_controller.update_manual_rule(claims, instance_id, status, service)