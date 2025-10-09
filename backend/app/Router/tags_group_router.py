# app/Router/tags_group_router.py
from __future__ import annotations

from fastapi import APIRouter, status

from app.Controllers import tags_group_controller

router = APIRouter(
    prefix="/tags-groups",
    tags=["Tags Groups"],
)

router.add_api_route(
    "/",
    tags_group_controller.create_tags_group,
    methods=["POST"],
    summary="Create a new Tags Group",
    status_code=status.HTTP_201_CREATED,
)
router.add_api_route(
    "/",
    tags_group_controller.list_tags_groups,
    methods=["GET"],
    summary="List all Tags Groups for the current user",
)
router.add_api_route(
    "/{tags_group_id}",
    tags_group_controller.get_tags_group,
    methods=["GET"],
    summary="Get a specific Tags Group by ID",
)
router.add_api_route(
    "/{tags_group_id}",
    tags_group_controller.update_tags_group,
    methods=["PUT"],
    summary="Update a Tags Group",
)
router.add_api_route(
    "/{tags_group_id}",
    tags_group_controller.delete_tags_group,
    methods=["DELETE"],
    summary="Delete a Tags Group",
)
router.add_api_route(
    "/reorder",
    tags_group_controller.reorder_tags_groups,
    methods=["PUT"],
    summary="Reorder Tags Groups",
    status_code=status.HTTP_200_OK,
)