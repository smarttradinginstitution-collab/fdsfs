from __future__ import annotations
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.Models.image import Image
from app.Schemas.image import ImageCreate

class ImageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, image_data: ImageCreate, general_account_id: uuid.UUID) -> Image:
        """
        Creates a new image record in the database.

        Args:
            image_data: The Pydantic schema containing the image metadata.
            general_account_id: The ID of the general account the image belongs to.

        Returns:
            The newly created Image SQLAlchemy object.
        """
        db_image = Image(
            **image_data.model_dump(),
            general_account_id=general_account_id
        )
        self.db.add(db_image)
        await self.db.commit()
        await self.db.refresh(db_image)
        return db_image