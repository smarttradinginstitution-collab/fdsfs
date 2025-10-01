from __future__ import annotations
from uuid import UUID
from fastapi import APIRouter, Depends, status
from app.Controllers.asset_controller import AssetController
from app.Schemas.asset import AssetRead, AssetCreate, AssetUpdate
from app.Router.auth import require_roles

router = APIRouter(
    prefix="/api/v1/assets",
    tags=["Assets"],
)

controller = AssetController()

# Publicly accessible for authenticated users
router.get("/", response_model=list[AssetRead])(controller.list_assets)
router.get("/{asset_id}", response_model=AssetRead)(controller.get_asset)

# Admin-only routes
admin_router = APIRouter(
    dependencies=[Depends(require_roles(["admin"]))],
)

admin_router.post(
    "/",
    response_model=AssetRead,
    status_code=status.HTTP_201_CREATED,
)(controller.create_asset)

admin_router.put("/{asset_id}", response_model=AssetRead)(controller.update_asset)

admin_router.delete(
    "/{asset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)(controller.delete_asset)

router.include_router(admin_router)