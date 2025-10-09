from __future__ import annotations
import uuid
from typing import Optional
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.Models.image import Image
from app.Schemas.image import ImageCreate

class ImageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_url(self, url: str) -> Optional[Image]:
        stmt = select(Image).where(Image.url == url)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_by_file_path(self, file_path: str) -> Optional[Image]:
        stmt = select(Image).where(Image.file_path == file_path)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create(self, image_data: ImageCreate, general_account_id: uuid.UUID) -> Image:
        """
        Creates a new image record in the database.

        Args:
            image_data: The Pydantic schema containing the image metadata.
            general_account_id: The ID of the general account the image belongs to.

        Returns:
            The newly created Image SQLAlchemy object.
        """
        if await self.get_by_url(image_data.url):
            raise HTTPException(
                status_code=409, detail="An image with this URL already exists."
            )
        if await self.get_by_file_path(image_data.file_path):
            raise HTTPException(
                status_code=409, detail="An image with this file path already exists."
            )

        db_image = Image(
            **image_data.model_dump(),
            general_account_id=general_account_id
        )
        self.db.add(db_image)
        await self.db.commit()
        await self.db.refresh(db_image)
        return db_image