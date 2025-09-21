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
async def test_sync_and_get_account_holdings_full_success(snaptrade_service: SnapTradeService):
    """
    Test the fully refactored method on a happy path, ensuring all 3 API calls
    are made and the service calls the repository layer with correctly processed data.
    """
    user_id, account_id, user_secret, symbol_id = uuid4(), uuid4(), "secret", uuid4()
    mock_user = AuthUser(id=user_id, profile=Profile(id=user_id, snaptrade_user_secret=user_secret))
    mock_account_from_db = BrokerageAccount(id=account_id, user_id=user_id, connection_id=uuid4())
    snaptrade_service.user_repo.get = AsyncMock(return_value=mock_user)

    mock_orders_response = [{"brokerage_order_id": "order1", "universal_symbol": {"symbol": "GOOG"}, "open_quantity": 5.0}]

    # We patch the repositories and the SnapTrade client
    with patch('app.Services.snaptrade_service.SnapTrade') as mock_snaptrade_client, \
         patch('app.Services.snaptrade_service.BrokerageAccountRepository') as mock_account_repo, \
         patch('app.Services.snaptrade_service.SecurityRepository') as mock_security_repo, \
         patch('app.Services.snaptrade_service.AccountOrderRepository') as mock_order_repo, \
         patch.object(snaptrade_service.db, 'commit', new_callable=AsyncMock), \
         patch.object(snaptrade_service.db, 'refresh', new_callable=AsyncMock):

        # Configure repository mocks
        mock_account_repo.return_value.get_by_id = AsyncMock(return_value=mock_account_from_db)
        mock_security_repo.return_value.upsert_securities = AsyncMock()
        mock_order_repo.build_orders_from_schemas.return_value = []

        # Configure API client mocks
        mock_api_client = mock_snaptrade_client.return_value.account_information
        mock_api_client.get_user_holdings = AsyncMock(return_value=MagicMock(body={}))
        mock_api_client.get_user_account_positions = AsyncMock(return_value=MagicMock(body=[]))
        mock_api_client.get_user_account_orders = AsyncMock(return_value=MagicMock(body=mock_orders_response))

        await snaptrade_service.sync_and_get_account_holdings(user_id, account_id)

        # Assert that the order repository's build method was called
        mock_order_repo.build_orders_from_schemas.assert_called_once()

        # Inspect the data passed to the repository method
        call_args = mock_order_repo.build_orders_from_schemas.call_args
        created_orders_schemas = call_args[0][1]
        assert len(created_orders_schemas) == 1
        assert created_orders_schemas[0].id == "order1"
        assert created_orders_schemas[0].open_quantity == 5.0

@pytest.mark.anyio
async def test_sync_and_get_account_holdings_with_option(snaptrade_service: SnapTradeService):
    """
    Test that an order with option data is processed correctly and passed to the repository.
    """
    user_id, account_id, user_secret, underlying_id = uuid4(), uuid4(), "secret", uuid4()
    mock_user = AuthUser(id=user_id, profile=Profile(id=user_id, snaptrade_user_secret=user_secret))
    mock_account_from_db = BrokerageAccount(id=account_id, user_id=user_id, connection_id=uuid4())
    snaptrade_service.user_repo.get = AsyncMock(return_value=mock_user)

    mock_option_order = {
        "brokerage_order_id": "option_order_1", "universal_symbol": {"symbol": "AAPL..."},
        "option_symbol": {
            "ticker": "AAPL251219C00200000", "strike_price": 200.0, "underlying_symbol": {"id": str(underlying_id)}
        }
    }

    with patch('app.Services.snaptrade_service.SnapTrade') as mock_snaptrade_client, \
         patch('app.Services.snaptrade_service.BrokerageAccountRepository') as mock_account_repo, \
         patch('app.Services.snaptrade_service.AccountOrderRepository') as mock_order_repo, \
         patch.object(snaptrade_service.db, 'commit', new_callable=AsyncMock), \
         patch.object(snaptrade_service.db, 'refresh', new_callable=AsyncMock):

        mock_account_repo.return_value.get_by_id = AsyncMock(return_value=mock_account_from_db)
        mock_order_repo.build_orders_from_schemas.return_value = []

        mock_api_client = mock_snaptrade_client.return_value.account_information
        mock_api_client.get_user_holdings = AsyncMock(return_value=MagicMock(body={}))
        mock_api_client.get_user_account_positions = AsyncMock(return_value=MagicMock(body=[]))
        mock_api_client.get_user_account_orders = AsyncMock(return_value=MagicMock(body=[mock_option_order]))

        await snaptrade_service.sync_and_get_account_holdings(user_id, account_id)

        mock_order_repo.build_orders_from_schemas.assert_called_once()
        created_orders_schemas = mock_order_repo.build_orders_from_schemas.call_args[0][1]

        assert len(created_orders_schemas) == 1
        option_details = created_orders_schemas[0].option_details
        assert option_details is not None
        assert option_details.option_ticker == "AAPL251219C00200000"
        assert option_details.underlying_security_id == underlying_id

@pytest.mark.anyio
async def test_sync_and_get_account_holdings_partial_failure(snaptrade_service: SnapTradeService):
    """
    Test that if one API call fails, the process continues and returns a warning.
    """
    user_id, account_id, user_secret = uuid4(), uuid4(), "secret"
    mock_user = AuthUser(id=user_id, profile=Profile(id=user_id, snaptrade_user_secret=user_secret))
    mock_account_from_db = BrokerageAccount(id=account_id, user_id=user_id, connection_id=uuid4(), orders=[], balances=[], positions=[])
    snaptrade_service.user_repo.get = AsyncMock(return_value=mock_user)

    with patch('app.Services.snaptrade_service.SnapTrade') as mock_snaptrade_client, \
         patch('app.Services.snaptrade_service.BrokerageAccountRepository') as mock_account_repo, \
         patch.object(snaptrade_service.db, 'commit', new_callable=AsyncMock), \
         patch.object(snaptrade_service.db, 'refresh', new_callable=AsyncMock):

        mock_account_repo.return_value.get_by_id = AsyncMock(return_value=mock_account_from_db)

        mock_api_client = mock_snaptrade_client.return_value.account_information
        mock_api_client.get_user_holdings = AsyncMock(return_value=MagicMock(body={}))
        mock_api_client.get_user_account_positions = AsyncMock(return_value=MagicMock(body=[]))
        mock_api_client.get_user_account_orders = AsyncMock(side_effect=Exception("API timeout"))

        result = await snaptrade_service.sync_and_get_account_holdings(user_id, account_id)

        assert result.warning is not None
        assert result.warning["warning"] == "partial_sync_failed"
        assert result.warning["failed_services"] == ["orders"]
        assert len(result.orders) == 0
