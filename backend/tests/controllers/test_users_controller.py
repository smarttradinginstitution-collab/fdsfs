import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.Controllers.users_controller import UsersController
from app.Schemas.auth_user import AuthUserCreate, AuthUserUpdate
from app.Models.auth_user import AuthUser

# ------------------------------
# Fixtures
# ------------------------------

@pytest.fixture
def users_controller():
    """Returns an instance of the UsersController."""
    return UsersController()

@pytest.fixture
def mock_db_session():
    """Provides a mock AsyncSession."""
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def mock_user_service(mocker):
    """Mocks the UserService."""
    return mocker.patch("app.Controllers.users_controller.UserService")

# ------------------------------
# list_users Tests
# ------------------------------

@pytest.mark.anyio
async def test_list_users_success(users_controller: UsersController, mock_db_session: AsyncSession, mock_user_service):
    """Test successful retrieval of all users."""
    user_id = uuid4()
    mock_users = [AuthUser(id=user_id, email="test@example.com")]
    mock_user_service.return_value.list_users = AsyncMock(return_value=mock_users)

    response = await users_controller.list_users(offset=0, limit=50, db=mock_db_session)

    assert len(response) == 1
    assert response[0].id == user_id
    assert response[0].email == "test@example.com"
    mock_user_service.return_value.list_users.assert_called_once_with(0, 50)

# ------------------------------
# get_user Tests
# ------------------------------

@pytest.mark.anyio
async def test_get_user_success(users_controller: UsersController, mock_db_session: AsyncSession, mock_user_service):
    """Test successful retrieval of a single user."""
    user_id = uuid4()
    mock_user = AuthUser(id=user_id, email="test@example.com")
    mock_user_service.return_value.get_user = AsyncMock(return_value=mock_user)

    response = await users_controller.get_user(user_id, mock_db_session)

    assert response.id == user_id
    assert response.email == "test@example.com"
    mock_user_service.return_value.get_user.assert_called_once_with(user_id)

@pytest.mark.anyio
async def test_get_user_not_found(users_controller: UsersController, mock_db_session: AsyncSession, mock_user_service):
    """Test retrieval of a non-existent user."""
    user_id = uuid4()
    mock_user_service.return_value.get_user = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc_info:
        await users_controller.get_user(user_id, mock_db_session)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "User non trovato" in exc_info.value.detail

# ------------------------------
# create_user Tests
# ------------------------------

@pytest.mark.anyio
async def test_create_user_success(users_controller: UsersController, mock_db_session: AsyncSession, mock_user_service):
    """Test successful creation of a new user."""
    user_id = uuid4()
    payload = AuthUserCreate(email="new@example.com", password="password")
    mock_created_user = AuthUser(id=user_id, email="new@example.com")
    mock_user_service.return_value.create_user_via_supabase = AsyncMock(return_value=mock_created_user)

    response = await users_controller.create_user(payload, mock_db_session)

    assert response.id == user_id
    assert response.email == "new@example.com"
    mock_user_service.return_value.create_user_via_supabase.assert_called_once_with(payload)

@pytest.mark.anyio
async def test_create_user_db_error(users_controller: UsersController, mock_db_session: AsyncSession, mock_user_service):
    """Test user creation failure if user not found in DB after creation."""
    payload = AuthUserCreate(email="new@example.com", password="password")
    mock_user_service.return_value.create_user_via_supabase = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc_info:
        await users_controller.create_user(payload, mock_db_session)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Creato su Supabase ma non trovato nel DB" in exc_info.value.detail

# ------------------------------
# update_user Tests
# ------------------------------

@pytest.mark.anyio
async def test_update_user_success(users_controller: UsersController, mock_db_session: AsyncSession, mock_user_service):
    """Test successful update of an existing user."""
    user_id = uuid4()
    payload = AuthUserUpdate(email="updated@example.com")
    mock_updated_user = AuthUser(id=user_id, email="updated@example.com")
    mock_user_service.return_value.update_user = AsyncMock(return_value=mock_updated_user)

    response = await users_controller.update_user(user_id, payload, mock_db_session)

    assert response.email == "updated@example.com"
    mock_user_service.return_value.update_user.assert_called_once_with(user_id, payload.model_dump(exclude_none=True))

@pytest.mark.anyio
async def test_update_user_not_found(users_controller: UsersController, mock_db_session: AsyncSession, mock_user_service):
    """Test updating a non-existent user."""
    user_id = uuid4()
    payload = AuthUserUpdate(email="updated@example.com")
    mock_user_service.return_value.update_user = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc_info:
        await users_controller.update_user(user_id, payload, mock_db_session)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "User non trovato" in exc_info.value.detail

# ------------------------------
# delete_user Tests
# ------------------------------

@pytest.mark.anyio
async def test_delete_user_success(users_controller: UsersController, mock_db_session: AsyncSession, mock_user_service):
    """Test successful deletion of a user."""
    user_id = uuid4()
    mock_user_service.return_value.delete_user = AsyncMock(return_value=True)

    response = await users_controller.delete_user(user_id, mock_db_session)

    assert response == {"deleted": True}
    mock_user_service.return_value.delete_user.assert_called_once_with(user_id)

@pytest.mark.anyio
async def test_delete_user_not_found(users_controller: UsersController, mock_db_session: AsyncSession, mock_user_service):
    """Test deleting a non-existent user."""
    user_id = uuid4()
    mock_user_service.return_value.delete_user = AsyncMock(return_value=False)

    with pytest.raises(HTTPException) as exc_info:
        await users_controller.delete_user(user_id, mock_db_session)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "User non trovato" in exc_info.value.detail
