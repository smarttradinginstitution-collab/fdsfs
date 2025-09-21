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
        mock_snaptrade_client.return_value.account_information.list_user_accounts.return_value = mock_api_response
        mock_account_repo.return_value.upsert_accounts = AsyncMock()
        mock_account_repo.return_value.get_accounts = AsyncMock(return_value=[mock_local_account])

        # Call the method
        result = await snaptrade_service.sync_and_get_user_accounts(user_id=user_id, connection_id=connection_id)

        # Assertions
        assert result["warning"] is None
        assert result["accounts"] == [mock_local_account]
        mock_snaptrade_client.return_value.account_information.list_user_accounts.assert_called_once()
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

        mock_snaptrade_client.return_value.account_information.list_user_accounts.side_effect = Exception("API Error")
        mock_account_repo.return_value.get_accounts = AsyncMock(return_value=mock_local_accounts)

        result = await snaptrade_service.sync_and_get_user_accounts(user_id=user_id)

        assert result["warning"] is not None
        assert result["warning"]["warning"] == "sync_failed"
        assert result["accounts"] == mock_local_accounts
        mock_account_repo.return_value.upsert_accounts.assert_not_called()


@pytest.mark.anyio
async def test_synchronize_connections_success(snaptrade_service: SnapTradeService):
    """
    Test successful synchronization of connections, iterating and upserting one by one.
    """
    user_id = uuid4()
    user_secret = "user_secret"
    mock_user = AuthUser(id=user_id, profile=Profile(id=user_id, snaptrade_user_secret=user_secret))

    snaptrade_service.user_repo = AsyncMock()
    snaptrade_service.user_repo.get.return_value = mock_user

    # Mock SnapTrade API response with two connections
    mock_api_response = MagicMock()
    mock_api_response.body = [
        {
            "id": "conn1", "brokerage": {"name": "Broker A"}, "created_date": "2023-01-01T12:00:00Z",
            "type": "read", "disabled": False, "disabled_date": None
        },
        {
            "id": "conn2", "brokerage": {"name": "Alpaca"}, "created_date": "2023-01-02T12:00:00Z",
            "type": "read", "disabled": False, "disabled_date": None
        }
    ]

    # Patch SnapTrade client and mock the database session execute and commit methods
    with patch('app.Services.snaptrade_service.SnapTrade') as mock_snaptrade_client, \
         patch.object(snaptrade_service.db, 'execute', new_callable=AsyncMock) as mock_db_execute, \
         patch.object(snaptrade_service.db, 'commit', new_callable=AsyncMock) as mock_db_commit:

        mock_snaptrade_client.return_value.connections.list_brokerage_authorizations.return_value = mock_api_response

        # Call the method
        result = await snaptrade_service.synchronize_connections(user_id=str(user_id))

        # Assertions
        assert result is True
        # Check that the API was called
        mock_snaptrade_client.return_value.connections.list_brokerage_authorizations.assert_called_once()

        # Check that db.execute was called for each connection
        assert mock_db_execute.call_count == 2

        # Check that the final commit was called
        mock_db_commit.assert_called_once()


@pytest.mark.anyio
async def test_sync_and_get_account_holdings_enrichment(snaptrade_service: SnapTradeService):
    """
    Test that sync_and_get_account_holdings correctly updates the account details.
    """
    user_id = uuid4()
    account_id = uuid4()
    user_secret = "user_secret"

    # Mock user and account from the database
    mock_user = AuthUser(id=user_id, profile=Profile(id=user_id, snaptrade_user_secret=user_secret))
    mock_account = BrokerageAccount(id=account_id, user_id=user_id)

    # Mock the user repository
    snaptrade_service.user_repo = AsyncMock()
    snaptrade_service.user_repo.get.return_value = mock_user

    # Mock SnapTrade API response
    mock_holdings_response = MagicMock()
    mock_holdings_response.body = {
        "account": {
            "id": str(account_id),
            "name": "Updated Name",
            "number": "999",
            "status": "open",
            "sync_status": {"holdings": {"last_successful_sync": "2025-01-01T12:00:00Z"}}
        },
        "positions": [],
        "balances": [],
        "orders": []
    }

    # Patch the SnapTrade client and the account repository
    with patch('app.Services.snaptrade_service.SnapTrade') as mock_snaptrade_client, \
         patch('app.Services.snaptrade_service.BrokerageAccountRepository') as mock_account_repo:

        # Configure mocks
        mock_account_repo.return_value.get_by_id.return_value = mock_account
        mock_snaptrade_client.return_value.account_information.get_user_holdings.return_value = mock_holdings_response
        mock_account_repo.return_value.update_account_details = AsyncMock()

        # Call the method
        await snaptrade_service.sync_and_get_account_holdings(user_id, account_id)

        # Assertions
        # Verify that get_by_id was called
        mock_account_repo.return_value.get_by_id.assert_called_once_with(account_id)

        # Verify that the update method was called
        mock_account_repo.return_value.update_account_details.assert_called_once()

        # Check the payload passed to the update method
        update_call_args = mock_account_repo.return_value.update_account_details.call_args
        update_payload = update_call_args[0][1] # Second argument of the call

        assert update_payload.name == "Updated Name"
        assert update_payload.number == "999"
        assert update_payload.status == "open"
        assert update_payload.sync_status is not None


@pytest.mark.anyio
async def test_sync_and_get_account_holdings_refactored(snaptrade_service: SnapTradeService):
    """
    Test the refactored sync_and_get_account_holdings method.
    Ensures it calls both /holdings and /positions endpoints and correctly
    upserts security and position data.
    """
    user_id = uuid4()
    account_id = uuid4()
    user_secret = "user_secret"
    symbol_id = uuid4()

    # Mock user and account
    mock_user = AuthUser(id=user_id, profile=Profile(id=user_id, snaptrade_user_secret=user_secret))
    mock_account = BrokerageAccount(id=account_id, user_id=user_id)

    snaptrade_service.user_repo = AsyncMock()
    snaptrade_service.user_repo.get.return_value = mock_user

    # Mock API responses
    mock_holdings_response = MagicMock()
    mock_holdings_response.body = {"account": {}, "balances": [], "orders": []} # No positions here

    mock_positions_response = MagicMock()
    mock_positions_response.body = [
        {
            "symbol": {
                "symbol": {
                    "id": str(symbol_id),
                    "symbol": "AAPL",
                    "description": "Apple Inc.",
                    "currency": {"code": "USD"},
                    "exchange": {"name": "NASDAQ"},
                    "figi_code": "BBG000B9XRY4",
                }
            },
            "units": 10, "price": 150.0, "currency": {"code": "USD"}
        }
    ]

    # Patch SnapTrade client and repositories
    with patch('app.Services.snaptrade_service.SnapTrade') as mock_snaptrade_client, \
         patch('app.Services.snaptrade_service.BrokerageAccountRepository') as mock_account_repo, \
         patch('app.Services.snaptrade_service.SecurityRepository') as mock_security_repo:

        # Configure mocks
        mock_account_repo.return_value.get_by_id.return_value = mock_account
        mock_security_repo.return_value.upsert_securities = AsyncMock()

        # Set up the two different API call mocks
        mock_api_client = mock_snaptrade_client.return_value.account_information
        mock_api_client.get_user_holdings.return_value = mock_holdings_response
        mock_api_client.get_user_account_positions.return_value = mock_positions_response

        # Call the method
        await snaptrade_service.sync_and_get_account_holdings(user_id, account_id)

        # Assertions
        mock_api_client.get_user_holdings.assert_called_once_with(user_id=str(user_id), user_secret=user_secret, account_id=str(account_id))
        mock_api_client.get_user_account_positions.assert_called_once_with(user_id=str(user_id), user_secret=user_secret, account_id=str(account_id))

        # Verify security upsert was called
        mock_security_repo.return_value.upsert_securities.assert_called_once()
        upsert_call_args = mock_security_repo.return_value.upsert_securities.call_args[0][0]
        assert len(upsert_call_args) == 1
        assert upsert_call_args[0].id == str(symbol_id)
        assert upsert_call_args[0].symbol == "AAPL"

        # Verify that the account object's positions relationship was updated
        # We can't easily check the call to build_positions_from_schemas as it's a static method
        # but we can check the final state of the account object before commit.
        # For that, we would need to mock db.add() and inspect the argument.
        # For this test, verifying the repository calls is sufficient.
