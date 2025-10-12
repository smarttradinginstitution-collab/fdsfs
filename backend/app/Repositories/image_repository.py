from __future__ import annotations
import uuid
from typing import Optional, List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.Models.image import Image
from app.Schemas.image import ImageCreate, ImageUpdate

class ImageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, image_id: uuid.UUID) -> Optional[Image]:
        """Gets an image by its ID."""
        return await self.db.get(Image, image_id)

    async def list_by_trade_id(self, trade_id: uuid.UUID) -> List[Image]:
        """Lists all images associated with a specific trade."""
        stmt = select(Image).where(Image.trade_id == trade_id).order_by(Image.created_at)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, image_data: ImageCreate) -> Image:
        """Creates a new image record in the database."""
        db_image = Image(**image_data.model_dump())
        self.db.add(db_image)
        await self.db.commit()
        await self.db.refresh(db_image)
        return db_image

    async def update(self, image_id: uuid.UUID, update_data: ImageUpdate) -> Optional[Image]:
        """Updates an image's metadata."""
        db_image = await self.get_by_id(image_id)
        if not db_image:
            return None

        update_values = update_data.model_dump(exclude_unset=True)
        for key, value in update_values.items():
            setattr(db_image, key, value)

        await self.db.commit()
        await self.db.refresh(db_image)
        return db_image

    async def delete(self, image_id: uuid.UUID) -> bool:
        """Deletes an image record from the database."""
        db_image = await self.get_by_id(image_id)
        if not db_image:
            return False

        await self.db.delete(db_image)
        await self.db.commit()
        return True