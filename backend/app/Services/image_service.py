from __future__ import annotations
import os
import uuid
from fastapi import Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.Infrastructure.db import get_db
from app.Repositories.image_repository import ImageRepository
from app.Repositories.general_account_repository import GeneralAccountRepository
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

    async def _get_general_account_id(self, user_id: uuid.UUID) -> uuid.UUID:
        general_account = await self.general_account_repo.get_by_user_id(user_id)
        if not general_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="General account not found for this user.",
            )
        return general_account.id

    async def upload_trade_image(
        self,
        *,
        file: UploadFile,
        user_id: uuid.UUID,
        trade_id: uuid.UUID,
        description: str | None = None,
        category: str | None = None,
        phase: str | None = None,
    ) -> Image:
        general_account_id = await self._get_general_account_id(user_id)

        # 1. Prepare file path for Supabase
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        storage_path = f"{general_account_id}/{trade_id}/{unique_filename}"

        # 2. Upload file to Supabase Storage
        try:
            file_content = await file.read()
            self.supabase.storage.from_(BUCKET_NAME).upload(
                path=storage_path,
                file=file_content,
                file_options={"content-type": file.content_type}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload image to storage: {e}",
            )

        # 3. Get public URL from Supabase
        try:
            public_url = self.supabase.storage.from_(BUCKET_NAME).get_public_url(storage_path)
        except Exception as e:
            # If URL generation fails, try to clean up the uploaded file
            self.supabase.storage.from_(BUCKET_NAME).remove([storage_path])
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get public URL for image: {e}",
            )

        # 4. Create database record
        image_data = ImageCreate(
            general_account_id=general_account_id,
            trade_id=trade_id,
            filename=file.filename,
            storage_path=storage_path,
            url=public_url,
            description=description,
            category=category,
            phase=phase,
        )

        db_image = await self.image_repo.create(image_data)
        return db_image

    async def get_images_for_trade(self, trade_id: uuid.UUID, requesting_user_id: uuid.UUID) -> list[Image]:
        # TODO: Add authorization check to ensure user can access this trade
        return await self.image_repo.list_by_trade_id(trade_id)

    async def update_image_metadata(self, image_id: uuid.UUID, update_data: ImageUpdate, requesting_user_id: uuid.UUID) -> Image:
        # TODO: Add authorization check
        updated_image = await self.image_repo.update(image_id, update_data)
        if not updated_image:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
        return updated_image

    async def delete_image(self, image_id: uuid.UUID, requesting_user_id: uuid.UUID) -> None:
        # 1. Get image from DB
        db_image = await self.image_repo.get_by_id(image_id)
        if not db_image:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

        # TODO: Add authorization check

        # 2. Delete file from Supabase Storage
        if db_image.storage_path:
            try:
                self.supabase.storage.from_(BUCKET_NAME).remove([db_image.storage_path])
            except Exception as e:
                # Log the error but proceed to delete the DB record anyway
                print(f"Warning: Failed to delete image {db_image.storage_path} from storage: {e}")

        # 3. Delete DB record
        await self.image_repo.delete(image_id)
        return