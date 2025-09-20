import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.Controllers.snaptrade_controller import SnapTradeController
from app.Services.snaptrade_service import SnapTradeConnectionError

@pytest.fixture
def snaptrade_controller():
    return SnapTradeController()

@pytest.fixture
def mock_db_session():
    return AsyncMock(spec=AsyncSession)

@pytest.mark.anyio
async def test_get_accounts_success(snaptrade_controller: SnapTradeController, mock_db_session: AsyncSession):
    """
    Test successful retrieval of accounts.
    """
    user_id = uuid4()
    claims = {"sub": str(user_id)}
    expected_result = {"accounts": [], "warning": None}

    with patch("app.Controllers.snaptrade_controller.SnapTradeService") as mock_snaptrade_service:
        mock_snaptrade_service.return_value.sync_and_get_user_accounts = AsyncMock(return_value=expected_result)

        response = await snaptrade_controller.get_accounts(
            db=mock_db_session,
            claims=claims
        )

        assert response == expected_result
        mock_snaptrade_service.return_value.sync_and_get_user_accounts.assert_called_once_with(
            user_id=user_id,
            connection_id=None
        )

@pytest.mark.anyio
async def test_get_accounts_with_connection_id(snaptrade_controller: SnapTradeController, mock_db_session: AsyncSession):
    """
    Test successful retrieval of accounts filtered by connection_id.
    """
    user_id = uuid4()
    connection_id = uuid4()
    claims = {"sub": str(user_id)}
    expected_result = {"accounts": [], "warning": None}

    with patch("app.Controllers.snaptrade_controller.SnapTradeService") as mock_snaptrade_service:
        mock_snaptrade_service.return_value.sync_and_get_user_accounts = AsyncMock(return_value=expected_result)

        await snaptrade_controller.get_accounts(
            connection_id=connection_id,
            db=mock_db_session,
            claims=claims
        )

        mock_snaptrade_service.return_value.sync_and_get_user_accounts.assert_called_once_with(
            user_id=user_id,
            connection_id=connection_id
        )

@pytest.mark.anyio
async def test_get_accounts_service_error(snaptrade_controller: SnapTradeController, mock_db_session: AsyncSession):
    """
    Test that a SnapTradeConnectionError from the service is handled correctly.
    """
    user_id = uuid4()
    claims = {"sub": str(user_id)}

    with patch("app.Controllers.snaptrade_controller.SnapTradeService") as mock_snaptrade_service:
        mock_snaptrade_service.return_value.sync_and_get_user_accounts.side_effect = SnapTradeConnectionError("Service Error")

        with pytest.raises(HTTPException) as exc_info:
            await snaptrade_controller.get_accounts(
                db=mock_db_session,
                claims=claims
            )

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Service Error" in exc_info.value.detail
