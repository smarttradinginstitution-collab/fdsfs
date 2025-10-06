from __future__ import annotations
from uuid import UUID
from fastapi import APIRouter, Depends, status, Response
from app.Controllers.asset_market_controller import AssetMarketController
from app.Schemas.asset_market import AssetMarketRead, AssetMarketCreate, AssetMarketUpdate
from app.Router.auth import require_roles, get_current_claims

router = APIRouter(
    prefix="/api/v1/asset-markets",
    tags=["Asset Markets"],
    # All routes in this router require a valid token.
    dependencies=[Depends(get_current_claims)],
)

controller = AssetMarketController()

# Routes for any authenticated user
router.get("/", response_model=list[AssetMarketRead])(controller.list_asset_markets)
router.get("/{asset_market_id}", response_model=AssetMarketRead)(controller.get_asset_market)

# Admin-only routes are grouped in a sub-router
admin_router = APIRouter(
    dependencies=[Depends(require_roles(["admin"]))],
)

admin_router.post(
    "/",
    response_model=AssetMarketRead,
    status_code=status.HTTP_201_CREATED,
)(controller.create_asset_market)

admin_router.put("/{asset_market_id}", response_model=AssetMarketRead)(controller.update_asset_market)

admin_router.delete(
    "/{asset_market_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)(controller.delete_asset_market)


# Include the admin routes in the main router
router.include_router(admin_router)