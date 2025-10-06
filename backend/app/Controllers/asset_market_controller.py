from fastapi import HTTPException, status
from uuid import UUID
from app.Repositories.asset_market_repository import AssetMarketRepository
from app.Schemas.asset_market import AssetMarketCreate, AssetMarketUpdate

class AssetMarketController:
    def __init__(self, repository: AssetMarketRepository):
        self.repo = repository

    async def create_market(self, market_data: AssetMarketCreate):
        # Check if a market with the same name already exists
        existing_market = await self.repo.get_by_name(market_data.name)
        if existing_market:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An asset market with this name already exists.",
            )
        return await self.repo.create(market_data)

    async def get_all_markets(self):
        return await self.repo.list()

    async def get_market_by_id(self, market_id: UUID):
        market = await self.repo.get(market_id)
        if not market:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset market not found.",
            )
        return market

    async def update_market(self, market_id: UUID, market_data: AssetMarketUpdate):
        # Check if the target market exists
        market = await self.repo.get(market_id)
        if not market:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset market not found.",
            )

        # If name is being updated, check for conflict
        if market_data.name and market_data.name != market.name:
            existing_market = await self.repo.get_by_name(market_data.name)
            if existing_market:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="An asset market with this name already exists.",
                )

        return await self.repo.update(market_id, market_data)

    async def delete_market(self, market_id: UUID):
        success = await self.repo.delete(market_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset market not found.",
            )
        return True