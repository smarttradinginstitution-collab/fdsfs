import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4, UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.Controllers.auth_controller import AuthController
from app.Schemas.auth_session import LoginInput, RegisterInput, VerifyMfaInput, MfaDisableInput
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
    response = await auth_controller.login(payload)

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
        await auth_controller.login(payload)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid credentials" in exc_info.value.detail

@pytest.mark.anyio
async def test_login_upstream_error_no_token(auth_controller: AuthController, mock_db_session: AsyncSession, mocker):
    """Test login failure when Supabase returns no access_token."""
    mock_supabase_service = mocker.patch("app.Controllers.auth_controller.supabase_service")

    mock_supabase_service.sign_in = AsyncMock(return_value={"user": {"id": str(uuid4())}})

    payload = LoginInput(email="test@example.com", password="password")

    with pytest.raises(HTTPException) as exc_info:
        await auth_controller.login(payload)

    assert exc_info.value.status_code == status.HTTP_502_BAD_GATEWAY
    assert "Login upstream non riuscito: access_token mancante" in exc_info.value.detail


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
    user_role_id = "0cc83a82-88f8-4ed9-9c92-ec9e09b266fd"

    mock_supabase_service.register_user = AsyncMock(return_value={
        "user": {"id": str(user_id), "email": "new_user@example.com"}
    })

    payload = RegisterInput(
        name="New User",
        email="new_user@example.com",
        password="password123",
        confirm_password="password123"
    )
    response = await auth_controller.register(payload, mock_db_session)

    assert response.status == "registered"
    assert response.user_id == str(user_id)
    mock_supabase_service.register_user.assert_called_once()
    mock_user_role_repo.assign.assert_called_once_with(user_id=user_id, role_id=UUID(user_role_id))


@pytest.mark.anyio
async def test_register_supabase_error(auth_controller: AuthController, mock_db_session: AsyncSession, mocker):
    """Test registration failure due to a Supabase error (e.g., user exists)."""
    mock_supabase_service = mocker.patch("app.Controllers.auth_controller.supabase_service")

    mock_supabase_service.register_user = AsyncMock(return_value={
        "error": "bad_request",
        "message": "User already registered"
    })

    payload = RegisterInput(
        name="Existing User",
        email="existing_user@example.com",
        password="password123",
        confirm_password="password123"
    )

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

    payload = RegisterInput(
        name="New User",
        email="new_user@example.com",
        password="password123",
        confirm_password="password123"
    )

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

    response = await auth_controller.logout(mock_claims)

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

    response = await auth_controller.logout(mock_claims)

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
        await auth_controller.logout(mock_claims)

    assert exc_info.value.status_code == status.HTTP_502_BAD_GATEWAY
    assert "Logout admin error 500" in exc_info.value.detail

@pytest.mark.anyio
async def test_logout_no_userid_in_claims(auth_controller: AuthController, mock_db_session: AsyncSession, mocker):
    """Test logout when the token claims do not contain a user ID."""
    mock_supabase_service = mocker.patch("app.Controllers.auth_controller.supabase_service")
    mock_supabase_service.admin_logout_user = AsyncMock()

    mock_claims = {"role": "user"}

    response = await auth_controller.logout(mock_claims)

    assert response.ok is True
    mock_supabase_service.admin_logout_user.assert_not_called()

@pytest.mark.anyio
async def test_register_integrity_error(auth_controller: AuthController, mock_db_session: AsyncSession, mocker):
    """Test that an IntegrityError during role assignment is handled gracefully."""
    mock_supabase_service = mocker.patch("app.Controllers.auth_controller.supabase_service")
    mock_user_role_repo = mocker.patch("app.Controllers.auth_controller.UserRoleRepository").return_value
    mock_user_role_repo.assign = AsyncMock(side_effect=IntegrityError(None, None, None))

    user_id = uuid4()
    user_role_id = UUID("0cc83a82-88f8-4ed9-9c92-ec9e09b266fd")

    mock_supabase_service.register_user = AsyncMock(return_value={
        "user": {"id": str(user_id), "email": "new_user@example.com"}
    })

    # Simulate an IntegrityError, which happens if the role is already assigned

    payload = RegisterInput(
        name="New User",
        email="new_user@example.com",
        password="password123",
        confirm_password="password123"
    )
    response = await auth_controller.register(payload, mock_db_session)

    # The registration should still be considered successful
    assert response.status == "registered"
    assert response.user_id == str(user_id)

# ------------------------------
# MFA Tests
# ------------------------------

@pytest.mark.anyio
async def test_login_mfa_required(auth_controller: AuthController, mocker):
    """Test login that requires an MFA challenge."""
    mock_supabase_service = mocker.patch("app.Controllers.auth_controller.supabase_service")
    mocker.patch("app.Controllers.auth_controller.jwt.get_unverified_claims", return_value={"aal": "aal1"})

    factor_id = f"factor_{uuid4()}"
    challenge_id = f"challenge_{uuid4()}"

    mock_supabase_service.sign_in = AsyncMock(return_value={
        "access_token": "aal1_token",
        "user": {
            "id": str(uuid4()),
            "factors": [{"id": factor_id, "factor_type": "totp", "status": "verified"}]
        }
    })
    mock_supabase_service.create_mfa_challenge = AsyncMock(return_value={"id": challenge_id})

    payload = LoginInput(email="mfa_user@example.com", password="password")
    response = await auth_controller.login(payload)

    assert response.status == "mfa_required"
    assert response.factor_id == factor_id
    assert response.challenge_id == challenge_id
    mock_supabase_service.create_mfa_challenge.assert_called_once_with("aal1_token", factor_id)


@pytest.mark.anyio
async def test_verify_mfa_success(auth_controller: AuthController, mocker):
    """Test successful MFA verification."""
    mock_supabase_service = mocker.patch("app.Controllers.auth_controller.supabase_service")
    mock_supabase_service.verify_mfa_challenge = AsyncMock(return_value={
        "access_token": "aal2_token",
        "token_type": "bearer",
        "user": {"mfa_status": "verified"}
    })

    payload = VerifyMfaInput(
        access_token="aal1_token",
        factor_id="factor_id",
        challenge_id="challenge_id",
        code="123456"
    )
    response = await auth_controller.verify_mfa(payload)

    assert response.access_token == "aal2_token"
    mock_supabase_service.verify_mfa_challenge.assert_called_once_with(
        "aal1_token", "factor_id", "challenge_id", "123456"
    )

@pytest.mark.anyio
async def test_verify_mfa_failure(auth_controller: AuthController, mocker):
    """Test failed MFA verification."""
    mock_supabase_service = mocker.patch("app.Controllers.auth_controller.supabase_service")
    mock_supabase_service.verify_mfa_challenge = AsyncMock(return_value={
        "error": "some_error",
        "message": "Codice OTP non valido"
    })

    payload = VerifyMfaInput(
        access_token="aal1_token",
        factor_id="factor_id",
        challenge_id="challenge_id",
        code="wrong_code"
    )
    with pytest.raises(HTTPException) as exc_info:
        await auth_controller.verify_mfa(payload)

    assert exc_info.value.status_code == 401
    assert "Codice OTP non valido" in exc_info.value.detail

@pytest.mark.anyio
async def test_enroll_totp_success(auth_controller: AuthController, mocker):
    """Test successful TOTP enrollment."""
    mock_supabase_service = mocker.patch("app.Controllers.auth_controller.supabase_service")

    factor_id = f"factor_{uuid4()}"
    challenge_id = f"challenge_{uuid4()}"
    mock_creds = MagicMock()
    mock_creds.credentials = "user_token"

    # Mock the user fetch call to return a confirmed user
    mock_supabase_service.get_user_from_access_token = AsyncMock(return_value={
        "id": str(uuid4()),
        "email_confirmed_at": "2023-01-01T12:00:00Z"
    })

    mock_supabase_service.enroll_totp = AsyncMock(return_value={
        "id": factor_id,
        "totp": {
            "secret": "SUPERSECRET",
            "uri": "otpauth://...",
            "qr_code": "<svg>...</svg>"
        }
    })
    mock_supabase_service.create_mfa_challenge = AsyncMock(return_value={"id": challenge_id})

    response = await auth_controller.enroll_totp(payload=None, creds=mock_creds)

    assert response.factor_id == factor_id
    assert response.secret == "SUPERSECRET"
    assert response.challenge_id == challenge_id
    mock_supabase_service.enroll_totp.assert_called_once()
    mock_supabase_service.create_mfa_challenge.assert_called_once_with("user_token", factor_id)


@pytest.mark.anyio
async def test_list_factors_success(auth_controller: AuthController, mocker):
    """Test successfully listing MFA factors."""
    mock_supabase_service = mocker.patch("app.Controllers.auth_controller.supabase_service")
    mock_creds = MagicMock()
    mock_creds.credentials = "user_token"

    factors_list = [{"id": "factor1", "status": "verified"}]
    mock_supabase_service.list_factors = AsyncMock(return_value={"factors": factors_list})

    response = await auth_controller.list_factors(creds=mock_creds)

    assert response.factors == factors_list
    mock_supabase_service.list_factors.assert_called_once_with("user_token")

@pytest.mark.anyio
async def test_delete_factor_success(auth_controller: AuthController, mocker):
    """Test successfully deleting an MFA factor."""
    mock_supabase_service = mocker.patch("app.Controllers.auth_controller.supabase_service")
    mock_creds = MagicMock()
    mock_creds.credentials = "user_token"
    factor_id = "factor_to_delete"

    mock_supabase_service.delete_mfa_factor = AsyncMock(return_value={"id": factor_id})

    response = await auth_controller.delete_factor(factor_id=factor_id, creds=mock_creds)

    assert response.ok is True
    mock_supabase_service.delete_mfa_factor.assert_called_once_with("user_token", factor_id)

@pytest.mark.anyio
async def test_disable_mfa_success(auth_controller: AuthController, mocker):
    """Test successful MFA disable with OTP verification."""
    mock_supabase_service = mocker.patch("app.Controllers.auth_controller.supabase_service")
    mock_creds = MagicMock()
    mock_creds.credentials = "user_token"

    user_id = str(uuid4())
    factor_id = f"factor_{uuid4()}"
    challenge_id = f"challenge_{uuid4()}"
    aal2_token = "new_aal2_token"

    # Mock the sequence of service calls
    mock_supabase_service.get_user_from_access_token = AsyncMock(side_effect = [
        # First call (to find the factor)
        {
            "id": user_id,
            "factors": [{"id": factor_id, "factor_type": "totp", "status": "verified"}]
        },
        # Second call (to get refreshed user state)
        {
            "id": user_id,
            "factors": []
        }
    ])
    mock_supabase_service.create_mfa_challenge = AsyncMock(return_value={"id": challenge_id})
    mock_supabase_service.verify_mfa_challenge = AsyncMock(return_value={
        "access_token": aal2_token,
            "token_type": "bearer",
            "expires_in": 3600,
            "refresh_token": "some_refresh_token",
        "user": {"id": user_id, "factors": []} # User object after unenroll
    })
    mock_supabase_service.delete_mfa_factor = AsyncMock(return_value={"id": factor_id})

    payload = MfaDisableInput(code="123456")
    response = await auth_controller.disable_mfa(payload=payload, creds=mock_creds)

    # Assertions
    assert mock_supabase_service.get_user_from_access_token.call_count == 2
    mock_supabase_service.get_user_from_access_token.assert_any_call("user_token")
    mock_supabase_service.get_user_from_access_token.assert_any_call(aal2_token)
    mock_supabase_service.create_mfa_challenge.assert_called_once_with("user_token", factor_id)
    mock_supabase_service.verify_mfa_challenge.assert_called_once_with("user_token", factor_id, challenge_id, "123456")
    mock_supabase_service.delete_mfa_factor.assert_called_once_with(aal2_token, factor_id)

    assert response.access_token == aal2_token
    assert response.user["id"] == user_id
    assert len(response.user["factors"]) == 0

@pytest.mark.anyio
async def test_enroll_totp_unconfirmed_email(auth_controller: AuthController, mocker):
    """Test that enrolling in MFA fails if the user's email is not confirmed."""
    mock_supabase_service = mocker.patch("app.Controllers.auth_controller.supabase_service")
    mock_creds = MagicMock()
    mock_creds.credentials = "user_token"

    # Mock a user without a confirmed email
    mock_supabase_service.get_user_from_access_token = AsyncMock(return_value={
        "id": str(uuid4()),
        "email": "unconfirmed@example.com",
        "email_confirmed_at": None
    })

    with pytest.raises(HTTPException) as exc_info:
        await auth_controller.enroll_totp(payload=None, creds=mock_creds)

    assert exc_info.value.status_code == 400
    assert "devi prima confermare il tuo indirizzo email" in exc_info.value.detail
