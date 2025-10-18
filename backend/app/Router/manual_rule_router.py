from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from app.Infrastructure.db import get_db
from app.Repositories.manual_rule_repository import ManualRuleRepository
from app.Router.dependencies import get_current_general_account_id
from app.Schemas.manual_rule_schema import ManualRuleRead, ManualRuleCreate, ManualRuleUpdate

router = APIRouter(
    prefix="/api/v1/manual-rules",
    tags=["Manual Rules"],
)

# Dependency for manual rule repository
def get_manual_rule_repo(db: AsyncSession = Depends(get_db)) -> ManualRuleRepository:
    return ManualRuleRepository(db)

@router.get("", response_model=List[ManualRuleRead])
async def list_manual_rules(
    general_account_id: UUID = Depends(get_current_general_account_id),
    repo: ManualRuleRepository = Depends(get_manual_rule_repo),
):
    return await repo.list_by_general_account(general_account_id)

@router.post("", response_model=ManualRuleRead, status_code=status.HTTP_201_CREATED)
async def create_manual_rule(
    rule_in: ManualRuleCreate,
    general_account_id: UUID = Depends(get_current_general_account_id),
    repo: ManualRuleRepository = Depends(get_manual_rule_repo),
):
    rule_data = rule_in.model_dump()
    rule_data["general_account_id"] = general_account_id
    return await repo.create(rule_data)

@router.put("/{rule_id}", response_model=ManualRuleRead)
async def update_manual_rule(
    rule_id: UUID,
    rule_in: ManualRuleUpdate,
    repo: ManualRuleRepository = Depends(get_manual_rule_repo),
):
    updated_rule = await repo.update(rule_id, rule_in)
    if not updated_rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return updated_rule

@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_manual_rule(
    rule_id: UUID,
    repo: ManualRuleRepository = Depends(get_manual_rule_repo),
):
    if not await repo.delete(rule_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")