# app/Controllers/rule_playbook_router.py
from __future__ import annotations

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends

from app.Controllers.rule_playbook_controller import RulePlaybookController
from app.Schemas.rule_playbook import RuleCreate, RuleRead, RuleUpdate, RuleReorder

# Controller instance
controller = RulePlaybookController()

# Router for rule-groups/{group_id}/rules
router = APIRouter(
    prefix="/rule-groups/{group_id}/rules",
    tags=["Playbook Rules"],
)

router.get(
    "/",
    response_model=List[RuleRead],
    summary="List rules for a group",
)(controller.list_rules_for_group)

router.post(
    "/",
    response_model=RuleRead,
    status_code=201,
    summary="Create a new rule for a group",
)(controller.create_rule_for_group)

router.put(
    "/reorder",
    status_code=200,
    summary="Reorder rules within a group",
    response_model=dict,
)(controller.reorder_rules)


# Router for individual rules (by rule ID)
# This is separate because it doesn't need the group_id in the path
router_by_id = APIRouter(
    prefix="/rules",
    tags=["Playbook Rules"],
)

router_by_id.put(
    "/{rule_id}",
    response_model=RuleRead,
    summary="Update a rule",
)(controller.update_rule)

router_by_id.delete(
    "/{rule_id}",
    status_code=200,
    summary="Delete a rule",
    response_model=dict,
)(controller.delete_rule)