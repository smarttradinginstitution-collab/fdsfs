import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.Repositories.image_repository import ImageRepository
from app.Models.image import Image
from app.Models.general_account import GeneralAccount
from app.Schemas.image import ImageCreate, ImageUpdate

pytestmark = pytest.mark.anyio

@pytest.fixture
async def setup_account(db_session: AsyncSession):
    """Fixture to create a general account."""
    user_id = uuid4()
    general_account = GeneralAccount(id=uuid4(), user_id=user_id, label="test_account_for_images")
    db_session.add(general_account)
    await db_session.commit()
    return general_account

@pytest.fixture
def image_repo(db_session: AsyncSession) -> ImageRepository:
    return ImageRepository(db_session)

async def test_create_image_raises_on_duplicate_path_or_url(image_repo: ImageRepository, setup_account):
    """Test that creating an image with a duplicate file_path or url raises an exception."""
    image_create_1 = ImageCreate(
        filename="image1.jpg",
        file_path="/path/to/image1.jpg",
        url="http://example.com/image1.jpg"
    )
    await image_repo.create(image_create_1, setup_account.id)

    # Duplicate file_path
    image_create_2 = ImageCreate(
        filename="image2.jpg",
        file_path="/path/to/image1.jpg",
        url="http://example.com/image2.jpg"
    )
    with pytest.raises(HTTPException) as exc_info:
        await image_repo.create(image_create_2, setup_account.id)
    assert exc_info.value.status_code == 409
    assert "already exists" in exc_info.value.detail

    # Duplicate url
    image_create_3 = ImageCreate(
        filename="image3.jpg",
        file_path="/path/to/image3.jpg",
        url="http://example.com/image1.jpg"
    )
    with pytest.raises(HTTPException) as exc_info:
        await image_repo.create(image_create_3, setup_account.id)
    assert exc_info.value.status_code == 409
    assert "already exists" in exc_info.value.detail

async def test_update_image_raises_on_duplicate_path_or_url(image_repo: ImageRepository, db_session: AsyncSession, setup_account):
    """Test that updating an image to a duplicate file_path or url raises an exception."""
    image1 = Image(
        id=uuid4(),
        general_account_id=setup_account.id,
        filename="img1.png",
        file_path="/path/img1.png",
        url="http://host/img1.png"
    )
    image2 = Image(
        id=uuid4(),
        general_account_id=setup_account.id,
        filename="img2.png",
        file_path="/path/img2.png",
        url="http://host/img2.png"
    )
    db_session.add_all([image1, image2])
    await db_session.commit()

    # Try to update image2's path to image1's path
    update_path = ImageUpdate(file_path="/path/img1.png")
    with pytest.raises(HTTPException) as exc_info:
        await image_repo.update(image2, update_path)
    assert exc_info.value.status_code == 409
    assert "file path already exists" in exc_info.value.detail

    # Try to update image2's url to image1's url
    update_url = ImageUpdate(url="http://host/img1.png")
    with pytest.raises(HTTPException) as exc_info:
        await image_repo.update(image2, update_url)
    assert exc_info.value.status_code == 409
    assert "URL already exists" in exc_info.value.detail