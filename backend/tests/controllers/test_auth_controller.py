import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.Controllers.auth_controller import AuthController
from app.Schemas.auth_session import LoginInput, RegisterInput
from app.config import settings

# ------------------------------
# Fixtures
# ------------------------------

@pytest.fixture
def auth_controller():
    """Returns an instance of the AuthController."""
    return AuthController()

@pytest.fixture
def mock_db_session():
    """Provides a mock AsyncSession."""
    return AsyncMock(spec=AsyncSession)

# ------------------------------
# LOGIN Tests
# ------------------------------

@pytest.mark.anyio
async def test_login_success(auth_controller: AuthController, mock_db_session: AsyncSession, mocker):
    """Test successful login."""
    mock_supabase_service = mocker.patch("app.Controllers.auth_controller.supabase_service")

    user_id = uuid4()
    mock_supabase_response = {
        "access_token": "fake_access_token",
        "token_type": "bearer",
        "expires_in": 3600,
        "refresh_token": "fake_refresh_token",
        "user": {"id": str(user_id), "email": "test@example.com"}
    }
    mock_supabase_service.sign_in = AsyncMock(return_value=mock_supabase_response)

    payload = LoginInput(email="test@example.com", password="password")
    response = await auth_controller.login(payload, mock_db_session)

    assert response.access_token == "fake_access_token"
    assert response.user["id"] == str(user_id)
    mock_supabase_service.sign_in.assert_called_once_with("test@example.com", "password")

@pytest.mark.anyio
async def test_login_invalid_credentials(auth_controller: AuthController, mock_db_session: AsyncSession, mocker):
    """Test login with invalid credentials."""
    mock_supabase_service = mocker.patch("app.Controllers.auth_controller.supabase_service")

    mock_supabase_service.sign_in = AsyncMock(return_value={
        "error": "invalid_grant",
        "message": "Invalid credentials"
    })

    payload = LoginInput(email="test@example.com", password="wrong_password")

    with pytest.raises(HTTPException) as exc_info:
        await auth_controller.login(payload, mock_db_session)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid credentials" in exc_info.value.detail

@pytest.mark.anyio
async def test_login_upstream_error_no_token(auth_controller: AuthController, mock_db_session: AsyncSession, mocker):
    """Test login failure when Supabase returns no access_token."""
    mock_supabase_service = mocker.patch("app.Controllers.auth_controller.supabase_service")

    mock_supabase_service.sign_in = AsyncMock(return_value={"user": {"id": str(uuid4())}})

    payload = LoginInput(email="test@example.com", password="password")

    with pytest.raises(HTTPException) as exc_info:
        await auth_controller.login(payload, mock_db_session)

    assert exc_info.value.status_code == status.HTTP_502_BAD_GATEWAY
    assert "Login upstream senza access_token" in exc_info.value.detail

@pytest.mark.anyio
async def test_login_dev_mode_error_message(auth_controller: AuthController, mock_db_session: AsyncSession, mocker):
    """Test that dev mode provides a more detailed error message."""
    mocker.patch.object(settings, 'ENV', 'dev')
    mock_supabase_service = mocker.patch("app.Controllers.auth_controller.supabase_service")

    mock_supabase_service.sign_in = AsyncMock(return_value={
        "error": "invalid_grant",
        "message": "Invalid credentials",
        "http_status": 400,
        "raw": {"error_description": "Invalid login credentials"}
    })

    payload = LoginInput(email="test@example.com", password="wrong_password")

    with pytest.raises(HTTPException) as exc_info:
        await auth_controller.login(payload, mock_db_session)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "http_status=400" in exc_info.value.detail
    assert "raw='Invalid login credentials'" in exc_info.value.detail

# ------------------------------
# REGISTER Tests
# ------------------------------

@pytest.mark.anyio
async def test_register_success(auth_controller: AuthController, mock_db_session: AsyncSession, mocker):
    """Test successful user registration and role assignment."""
    mock_supabase_service = mocker.patch("app.Controllers.auth_controller.supabase_service")
    mock_user_role_repo = mocker.patch("app.Controllers.auth_controller.UserRoleRepository").return_value
    mock_user_role_repo.assign = AsyncMock()

    user_id = uuid4()
    role_id = uuid4()

    mock_supabase_service.register_user = AsyncMock(return_value={
        "user": {"id": str(user_id), "email": "new_user@example.com"}
    })

    mock_role_result = MagicMock()
    mock_role_result.scalar_one_or_none.return_value = role_id
    mock_db_session.execute.return_value = mock_role_result

    payload = RegisterInput(email="new_user@example.com", password="password123")
    response = await auth_controller.register(payload, mock_db_session)

    assert response.status == "registered"
    assert response.user_id == str(user_id)
    mock_supabase_service.register_user.assert_called_once()
    mock_user_role_repo.assign.assert_called_once_with(user_id=user_id, role_id=role_id)

@pytest.mark.anyio
async def test_register_role_not_found(auth_controller: AuthController, mock_db_session: AsyncSession, mocker):
    """Test registration when the default 'user' role is not found."""
    mock_supabase_service = mocker.patch("app.Controllers.auth_controller.supabase_service")

    user_id = uuid4()
    mock_supabase_service.register_user = AsyncMock(return_value={
        "user": {"id": str(user_id), "email": "new_user@example.com"}
    })

    mock_role_result = MagicMock()
    mock_role_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_role_result

    payload = RegisterInput(email="new_user@example.com", password="password123")
    response = await auth_controller.register(payload, mock_db_session)

    assert response.status == "registered_but_role_missing:user"
    assert response.user_id == str(user_id)

@pytest.mark.anyio
async def test_register_supabase_error(auth_controller: AuthController, mock_db_session: AsyncSession, mocker):
    """Test registration failure due to a Supabase error (e.g., user exists)."""
    mock_supabase_service = mocker.patch("app.Controllers.auth_controller.supabase_service")

    mock_supabase_service.register_user = AsyncMock(return_value={
        "error": "bad_request",
        "message": "User already registered"
    })

    payload = RegisterInput(email="existing_user@example.com", password="password123")

    with pytest.raises(HTTPException) as exc_info:
        await auth_controller.register(payload, mock_db_session)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "User already registered" in exc_info.value.detail

@pytest.mark.anyio
async def test_register_supabase_no_userid(auth_controller: AuthController, mock_db_session: AsyncSession, mocker):
    """Test registration failure when Supabase returns no user ID."""
    mock_supabase_service = mocker.patch("app.Controllers.auth_controller.supabase_service")

    mock_supabase_service.register_user = AsyncMock(return_value={
        "user": {"email": "new_user@example.com"}
    })

    payload = RegisterInput(email="new_user@example.com", password="password123")

    with pytest.raises(HTTPException) as exc_info:
        await auth_controller.register(payload, mock_db_session)

    assert exc_info.value.status_code == status.HTTP_502_BAD_GATEWAY
    assert "user.id mancante" in exc_info.value.detail

# ------------------------------
# LOGOUT Tests
# ------------------------------

@pytest.mark.anyio
async def test_logout_success(auth_controller: AuthController, mock_db_session: AsyncSession, mocker):
    """Test successful logout."""
    mock_supabase_service = mocker.patch("app.Controllers.auth_controller.supabase_service")
    mock_supabase_service.admin_logout_user = AsyncMock(return_value={"ok": True})

    user_id = uuid4()
    mock_claims = {"sub": str(user_id)}

    response = await auth_controller.logout(mock_claims, mock_db_session)

    assert response.ok is True
    mock_supabase_service.admin_logout_user.assert_called_once_with(str(user_id))

@pytest.mark.anyio
@pytest.mark.parametrize("http_status", [400, 404, 409, 422])
async def test_logout_non_critical_error(auth_controller: AuthController, mock_db_session: AsyncSession, mocker, http_status):
    """Test that logout succeeds even with non-critical upstream errors."""
    mock_supabase_service = mocker.patch("app.Controllers.auth_controller.supabase_service")
    mock_supabase_service.admin_logout_user = AsyncMock(return_value={
        "error": "some_error",
        "message": "Some non-critical error",
        "http_status": http_status
    })

    user_id = uuid4()
    mock_claims = {"sub": str(user_id)}

    response = await auth_controller.logout(mock_claims, mock_db_session)

    assert response.ok is True

@pytest.mark.anyio
async def test_logout_critical_error(auth_controller: AuthController, mock_db_session: AsyncSession, mocker):
    """Test that logout fails on critical upstream errors."""
    mock_supabase_service = mocker.patch("app.Controllers.auth_controller.supabase_service")
    mock_supabase_service.admin_logout_user = AsyncMock(return_value={
        "error": "auth_error",
        "message": "Invalid JWT",
        "http_status": 500
    })

    user_id = uuid4()
    mock_claims = {"sub": str(user_id)}

    with pytest.raises(HTTPException) as exc_info:
        await auth_controller.logout(mock_claims, mock_db_session)

    assert exc_info.value.status_code == status.HTTP_502_BAD_GATEWAY
    assert "Logout admin error 500" in exc_info.value.detail

@pytest.mark.anyio
async def test_logout_no_userid_in_claims(auth_controller: AuthController, mock_db_session: AsyncSession, mocker):
    """Test logout when the token claims do not contain a user ID."""
    mock_supabase_service = mocker.patch("app.Controllers.auth_controller.supabase_service")
    mock_supabase_service.admin_logout_user = AsyncMock()

    mock_claims = {"role": "user"}

    response = await auth_controller.logout(mock_claims, mock_db_session)

    assert response.ok is True
    mock_supabase_service.admin_logout_user.assert_not_called()

@pytest.mark.anyio
async def test_register_integrity_error(auth_controller: AuthController, mock_db_session: AsyncSession, mocker):
    """Test that an IntegrityError during role assignment is handled gracefully."""
    mock_supabase_service = mocker.patch("app.Controllers.auth_controller.supabase_service")
    mock_user_role_repo = mocker.patch("app.Controllers.auth_controller.UserRoleRepository").return_value

    user_id = uuid4()
    role_id = uuid4()

    mock_supabase_service.register_user = AsyncMock(return_value={
        "user": {"id": str(user_id), "email": "new_user@example.com"}
    })

    mock_role_result = MagicMock()
    mock_role_result.scalar_one_or_none.return_value = role_id
    mock_db_session.execute.return_value = mock_role_result

    # Simulate an IntegrityError, which happens if the role is already assigned
    mock_user_role_repo.assign = AsyncMock(side_effect=IntegrityError(None, None, None))

    payload = RegisterInput(email="new_user@example.com", password="password123")
    response = await auth_controller.register(payload, mock_db_session)

    # The registration should still be considered successful
    assert response.status == "registered"
    assert response.user_id == str(user_id)

@pytest.mark.anyio
async def test_login_dev_mode_same_error_message(auth_controller: AuthController, mock_db_session: AsyncSession, mocker):
    """Test dev mode error message when raw message is the same."""
    mocker.patch.object(settings, 'ENV', 'dev')
    mock_supabase_service = mocker.patch("app.Controllers.auth_controller.supabase_service")

    mock_supabase_service.sign_in = AsyncMock(return_value={
        "error": "invalid_grant",
        "message": "Invalid credentials",
        "raw": {"error_description": "Invalid credentials"}
    })

    payload = LoginInput(email="test@example.com", password="wrong_password")

    with pytest.raises(HTTPException) as exc_info:
        await auth_controller.login(payload, mock_db_session)

    # The raw message should not be appended if it's the same
    assert exc_info.value.detail == "Invalid credentials"

@pytest.mark.anyio
async def test_login_dev_mode_none_raw_message(auth_controller: AuthController, mock_db_session: AsyncSession, mocker):
    """Test dev mode error message when raw message is None."""
    mocker.patch.object(settings, 'ENV', 'dev')
    mock_supabase_service = mocker.patch("app.Controllers.auth_controller.supabase_service")

    mock_supabase_service.sign_in = AsyncMock(return_value={
        "error": "invalid_grant",
        "message": "Invalid credentials",
        "raw": {"error_description": None}
    })

    payload = LoginInput(email="test@example.com", password="wrong_password")

    with pytest.raises(HTTPException) as exc_info:
        await auth_controller.login(payload, mock_db_session)

    assert "raw=" not in exc_info.value.detail

@pytest.mark.anyio
async def test_login_dev_mode_no_raw_message(auth_controller: AuthController, mock_db_session: AsyncSession, mocker):
    """Test dev mode error message when raw message is missing."""
    mocker.patch.object(settings, 'ENV', 'dev')
    mock_supabase_service = mocker.patch("app.Controllers.auth_controller.supabase_service")

    mock_supabase_service.sign_in = AsyncMock(return_value={
        "error": "invalid_grant",
        "message": "Invalid credentials",
        "http_status": 400,
        "raw": {}
    })

    payload = LoginInput(email="test@example.com", password="wrong_password")

    with pytest.raises(HTTPException) as exc_info:
        await auth_controller.login(payload, mock_db_session)

    assert "raw=" not in exc_info.value.detail
