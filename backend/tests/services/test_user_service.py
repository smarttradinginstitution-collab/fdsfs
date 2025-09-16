# backend/tests/services/test_user_service.py

import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.Services.user_service import UserService
from app.Schemas.auth_user import AuthUserCreate
from app.Models.auth_user import AuthUser


@pytest.fixture
def user_service(db_session: AsyncSession):
    # We will mock the repo attribute on the service instance in each test
    return UserService(db=db_session)


@pytest.mark.asyncio
async def test_create_user_via_supabase_success(user_service: UserService, mocker):
    # Arrange
    user_id = uuid4()
    mock_supabase_service = mocker.patch(
        "app.Services.user_service.supabase_service",
    )
    mock_supabase_service.register_user = AsyncMock(return_value={
        "user": {"id": str(user_id)}
    })

    # Mock the repo instance on the service
    user_service.repo = AsyncMock()

    expected_user = AuthUser(id=user_id, email="test@test.com")
    user_service.repo.get.return_value = expected_user

    payload = AuthUserCreate(
        email="test@test.com",
        password="password",
        user_meta={"name": "Test"},
        app_meta={"role": "user"},
        banned_until=None,
        phone="1234567890"
    )

    # Act
    result = await user_service.create_user_via_supabase(payload)

    # Assert
    assert result == expected_user
    mock_supabase_service.register_user.assert_called_once_with(
        email=payload.email,
        password=payload.password,
        user_meta=payload.user_meta,
        app_meta=payload.app_meta,
        banned_until=payload.banned_until,
        phone=payload.phone,
    )
    user_service.repo.get.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_create_user_via_supabase_supabase_error(user_service: UserService, mocker):
    # Arrange
    mock_supabase_service = mocker.patch(
        "app.Services.user_service.supabase_service",
    )
    mock_supabase_service.register_user = AsyncMock(return_value={
        "error": True, "message": "Supabase error"
    })
    user_service.repo = AsyncMock()

    payload = AuthUserCreate(email="test@test.com", password="password")

    # Act & Assert
    with pytest.raises(ValueError, match="Supabase register error: Supabase error"):
        await user_service.create_user_via_supabase(payload)

    user_service.repo.get.assert_not_called()


@pytest.mark.asyncio
async def test_create_user_via_supabase_no_user_id(user_service: UserService, mocker):
    # Arrange
    mock_supabase_service = mocker.patch(
        "app.Services.user_service.supabase_service",
    )
    mock_supabase_service.register_user = AsyncMock(return_value={"user": {}})
    user_service.repo = AsyncMock()

    payload = AuthUserCreate(email="test@test.com", password="password")

    # Act & Assert
    with pytest.raises(ValueError, match="Supabase response senza user.id"):
        await user_service.create_user_via_supabase(payload)

    user_service.repo.get.assert_not_called()


@pytest.mark.asyncio
async def test_list_users(user_service: UserService):
    # Arrange
    user_service.repo = AsyncMock()
    expected_users = [AuthUser(id=uuid4(), email="test1@test.com"), AuthUser(id=uuid4(), email="test2@test.com")]
    user_service.repo.list.return_value = expected_users

    # Act
    result = await user_service.list_users(offset=10, limit=20)

    # Assert
    assert result == expected_users
    user_service.repo.list.assert_called_once_with(10, 20)


@pytest.mark.asyncio
async def test_get_user(user_service: UserService):
    # Arrange
    user_id = uuid4()
    user_service.repo = AsyncMock()
    expected_user = AuthUser(id=user_id, email="test@test.com")
    user_service.repo.get.return_value = expected_user

    # Act
    result = await user_service.get_user(user_id)

    # Assert
    assert result == expected_user
    user_service.repo.get.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_update_user(user_service: UserService):
    # Arrange
    user_id = uuid4()
    user_data = {"email": "new@email.com"}
    user_service.repo = AsyncMock()
    updated_user = AuthUser(id=user_id, email="new@email.com")
    user_service.repo.update.return_value = updated_user

    # Act
    result = await user_service.update_user(user_id, user_data)

    # Assert
    assert result == updated_user
    user_service.repo.update.assert_called_once_with(user_id, user_data)


@pytest.mark.asyncio
async def test_delete_user(user_service: UserService):
    # Arrange
    user_id = uuid4()
    user_service.repo = AsyncMock()
    user_service.repo.delete.return_value = True

    # Act
    result = await user_service.delete_user(user_id)

    # Assert
    assert result is True
    user_service.repo.delete.assert_called_once_with(user_id)
