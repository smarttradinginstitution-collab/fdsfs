from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.Infrastructure.db import get_db
from app.Router.auth import require_roles, get_current_claims
from app.Repositories.asset_market_repository import AssetMarketRepository
from app.Controllers.asset_market_controller import AssetMarketController
from app.Schemas.asset_market import AssetMarketRead, AssetMarketCreate, AssetMarketUpdate

# Router for admin-only operations
admin_router = APIRouter(
    prefix="/asset-markets",
    tags=["Asset Markets"],
    dependencies=[Depends(require_roles(["admin"]))],
)

# Router for authenticated user operations
user_router = APIRouter(
    prefix="/asset-markets",
    tags=["Asset Markets"],
    dependencies=[Depends(get_current_claims)],
)

def get_asset_market_controller(db: AsyncSession = Depends(get_db)) -> AssetMarketController:
    repo = AssetMarketRepository(db)
    return AssetMarketController(repo)

@admin_router.post("/", response_model=AssetMarketRead, status_code=status.HTTP_201_CREATED)
async def create_asset_market(
    market_data: AssetMarketCreate,
    controller: AssetMarketController = Depends(get_asset_market_controller),
):
    """
    Create a new asset market. (Admin only)
    """
    return await controller.create_market(market_data)

@user_router.get("/", response_model=List[AssetMarketRead])
async def get_all_asset_markets(
    controller: AssetMarketController = Depends(get_asset_market_controller),
):
    """
    Get all asset markets. (Authenticated users)
    """
    return await controller.get_all_markets()

@user_router.get("/{market_id}", response_model=AssetMarketRead)
async def get_asset_market(
    market_id: UUID,
    controller: AssetMarketController = Depends(get_asset_market_controller),
):
    """
    Get a specific asset market by its ID. (Authenticated users)
    """
    return await controller.get_market_by_id(market_id)

@admin_router.put("/{market_id}", response_model=AssetMarketRead)
async def update_asset_market(
    market_id: UUID,
    market_data: AssetMarketUpdate,
    controller: AssetMarketController = Depends(get_asset_market_controller),
):
    """
    Update an asset market. (Admin only)
    """
    updated_market = await controller.update_market(market_id, market_data)
    if not updated_market:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset market not found")
    return updated_market

@admin_router.delete("/{market_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset_market(
    market_id: UUID,
    controller: AssetMarketController = Depends(get_asset_market_controller),
):
    """
    Delete an asset market. (Admin only)
    """
    await controller.delete_market(market_id)
    return None

# Combined router to be included in the main app
router = APIRouter()
router.include_router(admin_router)
router.include_router(user_router)