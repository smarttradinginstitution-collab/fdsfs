import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from app.Services.snaptrade_service import SnapTradeService
from app.Models.auth_user import AuthUser
from app.Models.profile import Profile
from app.Models.brokerage_account import BrokerageAccount

@pytest.fixture
def snaptrade_service(db_session: AsyncSession):
    # We pass a mock db_session because the service initializes repositories with it.
    # The actual repository methods will be mocked in the tests.
    return SnapTradeService(db=db_session)

@pytest.mark.anyio
async def test_sync_and_get_user_accounts_success(snaptrade_service: SnapTradeService):
    """
    Test successful synchronization of accounts.
    """
    user_id = uuid4()
    connection_id = uuid4()
    user_secret = "user_secret"

    # Mock user and profile
    mock_user = AuthUser(id=user_id, profile=Profile(id=user_id, snaptrade_user_secret=user_secret))
    # We mock the user repository method directly on the service instance
    snaptrade_service.user_repo = AsyncMock()
    snaptrade_service.user_repo.get.return_value = mock_user

    # Mock SnapTrade API response
    mock_snaptrade_account_dict = {
        "id": uuid4(),
        "brokerage_authorization": connection_id,
        "name": "Test Account",
        "number": "123",
        "institution_name": "Test Broker",
        "balance": {"total": {"amount": 1000, "currency": "USD"}}
    }
    mock_api_response = MagicMock()
    mock_api_response.body = [mock_snaptrade_account_dict]

    # Mock local DB accounts (as SQLAlchemy model instances)
    mock_local_account = BrokerageAccount(
        id=mock_snaptrade_account_dict["id"],
        user_id=user_id,
        connection_id=connection_id,
        name="Test Account", number="123", balance=1000, currency="USD", institution_name="Test Broker"
    )

    # Patch the SnapTrade client and the account repository
    with patch('app.Services.snaptrade_service.SnapTrade') as mock_snaptrade_client, \
         patch('app.Services.snaptrade_service.BrokerageAccountRepository') as mock_account_repo:

        # Configure mocks for the patched objects
        mock_snaptrade_client.return_value.account_information.get_all_user_holding_accounts.return_value = mock_api_response
        mock_account_repo.return_value.upsert_accounts = AsyncMock()
        mock_account_repo.return_value.get_accounts = AsyncMock(return_value=[mock_local_account])

        # Call the method
        result = await snaptrade_service.sync_and_get_user_accounts(user_id=user_id, connection_id=connection_id)

        # Assertions
        assert result["warning"] is None
        assert result["accounts"] == [mock_local_account]
        mock_snaptrade_client.return_value.account_information.get_all_user_holding_accounts.assert_called_once()
        mock_account_repo.return_value.upsert_accounts.assert_called_once()
        mock_account_repo.return_value.get_accounts.assert_called_once_with(user_id=user_id, connection_id=connection_id)


@pytest.mark.anyio
async def test_sync_and_get_user_accounts_api_error(snaptrade_service: SnapTradeService):
    """
    Test handling of SnapTrade API failure.
    """
    user_id = uuid4()
    user_secret = "user_secret"
    mock_user = AuthUser(id=user_id, profile=Profile(id=user_id, snaptrade_user_secret=user_secret))
    snaptrade_service.user_repo = AsyncMock()
    snaptrade_service.user_repo.get.return_value = mock_user

    # Mock empty local accounts to be returned on failure
    mock_local_accounts = []

    with patch('app.Services.snaptrade_service.SnapTrade') as mock_snaptrade_client, \
         patch('app.Services.snaptrade_service.BrokerageAccountRepository') as mock_account_repo:

        mock_snaptrade_client.return_value.account_information.get_all_user_holding_accounts.side_effect = Exception("API Error")
        mock_account_repo.return_value.get_accounts = AsyncMock(return_value=mock_local_accounts)

        result = await snaptrade_service.sync_and_get_user_accounts(user_id=user_id)

        assert result["warning"] is not None
        assert result["warning"]["warning"] == "sync_failed"
        assert result["accounts"] == mock_local_accounts
        mock_account_repo.return_value.upsert_accounts.assert_not_called()
