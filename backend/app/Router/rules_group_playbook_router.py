# app/Controllers/rules_group_playbook_router.py
from __future__ import annotations

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends

from app.Controllers.rules_group_playbook_controller import RulesGroupPlaybookController
from app.Schemas.rules_group_playbook import RulesGroupCreate, RulesGroupRead, RulesGroupUpdate, RulesGroupReorder

# Controller instance
controller = RulesGroupPlaybookController()

# Router for playbooks/{playbook_id}/rule-groups
router = APIRouter(
    prefix="/playbooks/{playbook_id}/rule-groups",
    tags=["Playbook Rule Groups"],
)

router.get(
    "/",
    response_model=List[RulesGroupRead],
    summary="List rule groups for a playbook",
)(controller.list_groups_for_playbook)

router.post(
    "/",
    response_model=RulesGroupRead,
    status_code=201,
    summary="Create a new rule group for a playbook",
)(controller.create_group_for_playbook)

router.put(
    "/reorder",
    status_code=200,
    summary="Reorder rule groups for a playbook",
    response_model=dict,
)(controller.reorder_groups)


# Router for individual rule groups (by group ID)
# This is separate because it doesn't need the playbook_id in the path
router_by_id = APIRouter(
    prefix="/rule-groups",
    tags=["Playbook Rule Groups"],
)

router_by_id.put(
    "/{group_id}",
    response_model=RulesGroupRead,
    summary="Update a rule group",
)(controller.update_group)

router_by_id.delete(
    "/{group_id}",
    status_code=200,
    summary="Delete a rule group",
    response_model=dict,
)(controller.delete_group)