from __future__ import annotations
from uuid import UUID
from fastapi import APIRouter, Depends, status
from app.Controllers.asset_alias_controller import AssetAliasController
from app.Schemas.asset_alias import AssetAliasRead, AssetAliasCreate, AssetAliasUpdate
from app.Router.auth import require_roles

router = APIRouter(
    prefix="/api/v1/asset-aliases",
    tags=["Asset Aliases"],
    dependencies=[Depends(require_roles(["admin"]))],
)

controller = AssetAliasController()

router.get("/", response_model=list[AssetAliasRead])(controller.list_aliases)
router.get("/{alias_id}", response_model=AssetAliasRead)(controller.get_alias)

router.post(
    "/",
    response_model=AssetAliasRead,
    status_code=status.HTTP_201_CREATED,
)(controller.create_alias)

router.put("/{alias_id}", response_model=AssetAliasRead)(controller.update_alias)

router.delete(
    "/{alias_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)(controller.delete_alias)


# Also add a nested route under assets to list aliases for a specific asset
asset_nested_router = APIRouter(
    prefix="/api/v1/assets/{asset_id}/aliases",
    tags=["Assets"],
    dependencies=[Depends(require_roles(["admin"]))],
)

asset_nested_router.get("/", response_model=list[AssetAliasRead])(
    controller.list_aliases_for_asset
)