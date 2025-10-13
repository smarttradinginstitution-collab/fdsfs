from __future__ import annotations
import os
import uuid
from fastapi import Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.Infrastructure.db import get_db
from app.Repositories.image_repository import ImageRepository
from app.Repositories.general_account_repository import GeneralAccountRepository
from app.Repositories.trade_repository import TradeRepository
from app.Schemas.image import ImageCreate, ImageUpdate
from app.Models.image import Image
from app.Services.supabase_client import get_supabase_client, SupabaseClient

BUCKET_NAME = "trade_images"

class ImageService:
    def __init__(
        self,
        db: AsyncSession = Depends(get_db),
        supabase: SupabaseClient = Depends(get_supabase_client),
    ):
        self.db = db
        self.supabase = supabase
        self.image_repo = ImageRepository(db)
        self.general_account_repo = GeneralAccountRepository(db)
        self.trade_repo = TradeRepository(db)

    async def _get_general_account_id(self, user_id: uuid.UUID) -> uuid.UUID:
        general_account = await self.general_account_repo.get_by_user_id(user_id)
        if not general_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="General account not found for this user.",
            )
        return general_account.id

    async def _authorize_user_for_trade(self, user_id: uuid.UUID, trade_id: uuid.UUID):
        general_account_id = await self._get_general_account_id(user_id)
        trade = await self.trade_repo.get_by_id_and_general_account(trade_id, general_account_id)
        if not trade:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not have access to this trade.")
        return trade

    async def _authorize_user_for_image(self, user_id: uuid.UUID, image_id: uuid.UUID) -> Image:
        image = await self.image_repo.get_by_id(image_id)
        if not image:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
        if not image.trade_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image is not associated with a trade.")

        await self._authorize_user_for_trade(user_id, image.trade_id)
        return image

    async def upload_trade_image(
        self, *, file: UploadFile, user_id: uuid.UUID, trade_id: uuid.UUID,
        description: str | None = None, category: str | None = None, phase: str | None = None,
    ) -> Image:
        trade = await self._authorize_user_for_trade(user_id, trade_id)
        general_account_id = trade.trading_account.general_account_id

        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        storage_path = f"{general_account_id}/{trade_id}/{unique_filename}"

        try:
            file_content = await file.read()
            self.supabase.storage.from_(BUCKET_NAME).upload(
                path=storage_path, file=file_content, file_options={"content-type": file.content_type}
            )
            public_url = self.supabase.storage.from_(BUCKET_NAME).get_public_url(storage_path)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Storage operation failed: {e}")

        image_data = ImageCreate(
            general_account_id=general_account_id, trade_id=trade_id, filename=file.filename,
            storage_path=storage_path, url=public_url, description=description, category=category, phase=phase,
        )
        return await self.image_repo.create(image_data)

    async def get_images_for_trade(self, trade_id: uuid.UUID, requesting_user_id: uuid.UUID) -> list[Image]:
        await self._authorize_user_for_trade(requesting_user_id, trade_id)
        return await self.image_repo.list_by_trade_id(trade_id)

    async def update_image_metadata(self, image_id: uuid.UUID, update_data: ImageUpdate, requesting_user_id: uuid.UUID) -> Image:
        await self._authorize_user_for_image(requesting_user_id, image_id)
        updated_image = await self.image_repo.update(image_id, update_data)
        if not updated_image:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found after update")
        return updated_image

    async def delete_image(self, image_id: uuid.UUID, requesting_user_id: uuid.UUID) -> None:
        db_image = await self._authorize_user_for_image(requesting_user_id, image_id)

        if db_image.storage_path:
            try:
                self.supabase.storage.from_(BUCKET_NAME).remove([db_image.storage_path])
            except Exception as e:
                print(f"Warning: Failed to delete image {db_image.storage_path} from storage: {e}")

        await self.image_repo.delete(image_id)
        return