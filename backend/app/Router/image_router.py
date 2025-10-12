from __future__ import annotations
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from app.Services.image_service import ImageService
from app.Schemas.image import ImageRead, ImageUpdate
from app.Router.dependencies import get_current_user, CurrentUser

router = APIRouter(prefix="/api/v1/images", tags=["Images"])


@router.patch("/{image_id}", response_model=ImageRead)
async def update_image_metadata(
    image_id: uuid.UUID,
    update_data: ImageUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    image_service: ImageService = Depends(),
) -> ImageRead:
    """
    Updates an image's metadata (description, category, etc.).
    """
    # Authorization to update should be handled within the service
    updated_image = await image_service.update_image_metadata(
        image_id=image_id,
        update_data=update_data,
        requesting_user_id=current_user.id
    )
    return updated_image

@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    image_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    image_service: ImageService = Depends(),
):
    """
    Deletes an image from storage and the database.
    """
    # Authorization to delete should be handled within the service
    await image_service.delete_image(
        image_id=image_id,
        requesting_user_id=current_user.id
    )
    return None