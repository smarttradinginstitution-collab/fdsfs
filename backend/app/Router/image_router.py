from __future__ import annotations
from fastapi import APIRouter, Depends, UploadFile, File
from app.Services.image_service import ImageService
from app.Schemas.image import ImageRead
from app.Router.dependencies import get_current_user, CurrentUser

router = APIRouter(prefix="/api/v1/images", tags=["Images"])

@router.post("/upload", response_model=ImageRead)
async def upload_image(
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(get_current_user),
    image_service: ImageService = Depends(),
) -> ImageRead:
    """
    Uploads an image, saves it to the server, and creates a corresponding
    database record.
    """
    db_image = await image_service.upload_image(file=file, user_id=current_user.id)
    return db_image