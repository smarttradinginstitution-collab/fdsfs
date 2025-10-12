from __future__ import annotations
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from app.Services.image_service import ImageService
from app.Schemas.image import ImageRead, ImageUpdate
from app.Router.dependencies import get_current_user, CurrentUser

# This router will be included with the /api/v1 prefix
router = APIRouter(tags=["Images"])

# Note: The paths here are relative to where they are included.
# We will include some under /trades/{trade_id} and others under /images

# To be included in `trades_router`
trade_image_router = APIRouter()

@trade_image_router.post("/images", response_model=ImageRead, status_code=status.HTTP_201_CREATED)
async def upload_trade_image(
    trade_id: uuid.UUID,
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    phase: Optional[str] = Form(None),
    current_user: CurrentUser = Depends(get_current_user),
    image_service: ImageService = Depends(),
):
    return await image_service.upload_trade_image(
        file=file,
        user_id=current_user.id,
        trade_id=trade_id,
        description=description,
        category=category,
        phase=phase,
    )

@trade_image_router.get("/images", response_model=List[ImageRead])
async def get_trade_images(
    trade_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    image_service: ImageService = Depends(),
):
    return await image_service.get_images_for_trade(trade_id, requesting_user_id=current_user.id)

# To be included at the root level under /images
image_metadata_router = APIRouter(prefix="/images")

@image_metadata_router.patch("/{image_id}", response_model=ImageRead)
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

@image_metadata_router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
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