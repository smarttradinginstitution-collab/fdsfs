from __future__ import annotations
import os
import uuid
from fastapi import Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Repositories.image_repository import ImageRepository
from app.Repositories.general_account_repository import GeneralAccountRepository
from app.Schemas.image import ImageCreate
from app.Models.image import Image

UPLOAD_DIRECTORY = "static/uploads/images"

class ImageService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
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

    async def upload_image(self, file: UploadFile, user_id: uuid.UUID) -> Image:
        # 1. Ensure the user has a general account
        general_account_id = await self._get_general_account_id(user_id)

        # 2. Create the upload directory if it doesn't exist
        os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

        # 3. Generate a unique filename to prevent collisions
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        file_path = os.path.join(UPLOAD_DIRECTORY, unique_filename)

        # 4. Save the file to the server
        try:
            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())
        except Exception as e:
            # Handle potential file writing errors
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not save file: {e}",
            )

        # 5. Create the public URL for the image
        # This assumes the 'static' directory is served at the root of the domain.
        # e.g., http://localhost:8000/uploads/images/your_image.jpg
        url = f"/uploads/images/{unique_filename}"

        # 6. Create the Pydantic schema for the new image record
        image_data = ImageCreate(
            filename=file.filename,
            file_path=file_path,
            url=url
        )

        # 7. Save the image metadata to the database
        db_image = await self.image_repo.create(image_data, general_account_id)
        return db_image