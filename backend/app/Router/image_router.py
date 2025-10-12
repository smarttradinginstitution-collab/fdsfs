from __future__ import annotations
import uuid
from fastapi import APIRouter, Depends, status, UploadFile, File
from app.Services.image_service import ImageService
from app.Schemas.image import ImageRead, ImageUpdate
from app.Router.dependencies import get_current_user, CurrentUser

router = APIRouter(prefix="/images", tags=["Images"])

@router.patch("/{image_id}", response_model=ImageRead)
async def update_image_metadata(
    image_id: uuid.UUID,
    update_data: ImageUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    image_service: ImageService = Depends(),
) -> ImageRead:
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
    await image_service.delete_image(
        image_id=image_id,
        requesting_user_id=current_user.id
    )
    return None

@router.post("/{image_id}/replace", response_model=ImageRead)
async def replace_image(
    image_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(get_current_user),
    image_service: ImageService = Depends(),
) -> ImageRead:
    """
    Replaces an existing image with a new one (e.g., after annotation).
    """
    return await image_service.replace_image(
        image_id=image_id,
        file=file,
        user_id=current_user.id
    )