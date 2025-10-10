from __future__ import annotations
import uuid
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.Models.image import Image
from app.Schemas.image import ImageCreate, ImageUpdate

class ImageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, image_id: uuid.UUID) -> Optional[Image]:
        """Gets an image by its ID."""
        return await self.db.get(Image, image_id)

    async def create(self, image_data: ImageCreate, general_account_id: uuid.UUID) -> Image:
        """
        Creates a new image record in the database.
        """
        stmt = select(Image).where(
            or_(
                Image.file_path == image_data.file_path,
                Image.url == image_data.url
            )
        )
        existing_image = await self.db.execute(stmt)
        if existing_image.scalars().first():
            raise HTTPException(
                status_code=409,
                detail="An image with this file path or URL already exists.",
            )

        db_image = Image(
            **image_data.model_dump(),
            general_account_id=general_account_id
        )
        self.db.add(db_image)
        await self.db.commit()
        await self.db.refresh(db_image)
        return db_image

    async def update(self, db_obj: Image, image_data: ImageUpdate) -> Image:
        """Updates an existing image."""
        update_data = image_data.model_dump(exclude_unset=True)
        if not update_data:
            return db_obj

        if "file_path" in update_data and update_data["file_path"] != db_obj.file_path:
            stmt = select(Image).where(
                Image.file_path == update_data["file_path"],
                Image.id != db_obj.id
            )
            existing_image = await self.db.execute(stmt)
            if existing_image.scalars().first():
                raise HTTPException(
                    status_code=409,
                    detail="An image with this file path already exists.",
                )

        if "url" in update_data and update_data["url"] != db_obj.url:
            stmt = select(Image).where(
                Image.url == update_data["url"],
                Image.id != db_obj.id
            )
            existing_image = await self.db.execute(stmt)
            if existing_image.scalars().first():
                raise HTTPException(
                    status_code=409,
                    detail="An image with this URL already exists.",
                )

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj