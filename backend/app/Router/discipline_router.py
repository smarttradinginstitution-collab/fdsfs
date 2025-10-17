# backend/app/Router/discipline_router.py
from __future__ import annotations

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends

from app.Controllers.discipline_controller import DisciplineController
from app.Services.discipline_service import DisciplineService
from app.Schemas.discipline_rule import (
    DisciplineRuleRead,
    DisciplineRuleCreate,
    DisciplineRuleUpdate,
)
from app.Router.auth import get_current_claims

router = APIRouter(
    prefix="/discipline",
    tags=["Discipline"],
    dependencies=[Depends(get_current_claims)],
)

discipline_controller = DisciplineController()


@router.get("/rules", response_model=List[DisciplineRuleRead])
async def get_all_rules(
    claims: dict = Depends(get_current_claims),
    service: DisciplineService = Depends(),
):
    return await discipline_controller.get_all_rules(claims, service)


@router.post("/rules", response_model=DisciplineRuleRead, status_code=201)
async def create_rule(
    rule_create: DisciplineRuleCreate,
    claims: dict = Depends(get_current_claims),
    service: DisciplineService = Depends(),
):
    return await discipline_controller.create_rule(claims, rule_create, service)


@router.put("/rules/{rule_id}", response_model=DisciplineRuleRead)
async def update_rule(
    rule_id: UUID,
    rule_update: DisciplineRuleUpdate,
    claims: dict = Depends(get_current_claims),
    service: DisciplineService = Depends(),
):
    return await discipline_controller.update_rule(claims, rule_id, rule_update, service)


@router.delete("/rules/{rule_id}", status_code=204)
async def delete_rule(
    rule_id: UUID,
    claims: dict = Depends(get_current_claims),
    service: DisciplineService = Depends(),
):
    await discipline_controller.delete_rule(claims, rule_id, service)
    return None