import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException, UploadFile

from app.Models.image import Image
from app.Services.image_service import ImageService
from app.Repositories.image_repository import ImageRepository
from app.Repositories.general_account_repository import GeneralAccountRepository

@pytest.fixture
def mock_supabase_client():
    """Mocks the Supabase client with chained mocks."""
    mock_client = MagicMock()
    mock_storage = MagicMock()
    mock_bucket = MagicMock()
    mock_bucket.upload = MagicMock()
    mock_bucket.get_public_url.return_value = "http://example.com/test.png"
    mock_bucket.remove = MagicMock()
    mock_storage.from_.return_value = mock_bucket
    mock_client.storage = mock_storage
    return mock_client

@pytest.fixture
def mock_db_session():
    """Provides a mock for the database session."""
    return AsyncMock()

@pytest.fixture
def image_service(mock_db_session, mock_supabase_client):
    """
    Provides an ImageService instance with its repository dependencies correctly mocked.
    """
    # Instantiate the service with the mocked db and supabase client
    service = ImageService(db=mock_db_session, supabase=mock_supabase_client)

    # Manually replace the repository instances with AsyncMocks specced from the real classes.
    # This is the correct way to ensure they are awaitable and have the right API.
    service.image_repo = AsyncMock(spec=ImageRepository)
    service.general_account_repo = AsyncMock(spec=GeneralAccountRepository)

    return service

@pytest.mark.asyncio
async def test_upload_trade_image_success(image_service: ImageService, mock_supabase_client):
    """Test successful image upload and creation."""
    # Arrange
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test.png"
    mock_file.content_type = "image/png"
    mock_file.read = AsyncMock(return_value=b"test_data")

    user_id = uuid.uuid4()
    trade_id = uuid.uuid4()

    # Configure the mock return values
    image_service.general_account_repo.get_by_user_id.return_value = MagicMock(id=uuid.uuid4())
    image_service.image_repo.create.return_value = Image(id=uuid.uuid4())

    # Act
    result = await image_service.upload_trade_image(
        file=mock_file,
        user_id=user_id,
        trade_id=trade_id,
        description="A test image"
    )

    # Assert
    assert result is not None
    image_service.general_account_repo.get_by_user_id.assert_awaited_once_with(user_id)
    mock_supabase_client.storage.from_("trade_images").upload.assert_called_once()
    image_service.image_repo.create.assert_awaited_once()

@pytest.mark.asyncio
async def test_delete_image_success(image_service: ImageService, mock_supabase_client):
    """Test successful image deletion from DB and storage."""
    # Arrange
    image_id = uuid.uuid4()
    user_id = uuid.uuid4()
    storage_path = f"some/path/{image_id}.png"

    # Configure the mock to return a valid image object
    image_service.image_repo.get_by_id.return_value = Image(id=image_id, storage_path=storage_path)

    # Act
    await image_service.delete_image(image_id=image_id, requesting_user_id=user_id)

    # Assert
    image_service.image_repo.get_by_id.assert_awaited_once_with(image_id)
    mock_supabase_client.storage.from_("trade_images").remove.assert_called_once_with([storage_path])
    image_service.image_repo.delete.assert_awaited_once_with(image_id)

@pytest.mark.asyncio
async def test_delete_image_not_found_raises_exception(image_service: ImageService):
    """Test that trying to delete a non-existent image raises a 404 HTTPException."""
    # Arrange
    image_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Configure the mock to simulate the image not being found
    image_service.image_repo.get_by_id.return_value = None

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await image_service.delete_image(image_id=image_id, requesting_user_id=user_id)

    assert exc_info.value.status_code == 404
    image_service.image_repo.get_by_id.assert_awaited_once_with(image_id)