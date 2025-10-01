from __future__ import annotations
from uuid import UUID
from fastapi import APIRouter, Depends, status
from app.Controllers.asset_class_controller import AssetClassController
from app.Schemas.asset_class import AssetClassRead, AssetClassCreate, AssetClassUpdate
from app.Router.auth import require_roles

router = APIRouter(
    prefix="/api/v1/asset-classes",
    tags=["Asset Classes"],
)

controller = AssetClassController()

# Publicly accessible for authenticated users
router.get("/", response_model=list[AssetClassRead])(controller.list_asset_classes)
router.get("/{asset_class_id}", response_model=AssetClassRead)(controller.get_asset_class)

# Admin-only routes
admin_router = APIRouter(
    dependencies=[Depends(require_roles(["admin"]))],
)

admin_router.post(
    "/",
    response_model=AssetClassRead,
    status_code=status.HTTP_201_CREATED,
)(controller.create_asset_class)

admin_router.put("/{asset_class_id}", response_model=AssetClassRead)(controller.update_asset_class)

admin_router.delete(
    "/{asset_class_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)(controller.delete_asset_class)

router.include_router(admin_router)