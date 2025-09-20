import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from app.Models.brokerage_account import BrokerageAccount
from app.Repositories.brokerage_account_repository import BrokerageAccountRepository

@pytest.mark.anyio
async def test_upsert_accounts():
    """
    Test that upsert_accounts correctly calls the insert statement with on_conflict_do_update.
    """
    mock_session = AsyncMock(spec=AsyncSession)
    repo = BrokerageAccountRepository(mock_session)

    accounts_data = [
        {
            "id": uuid4(),
            "user_id": uuid4(),
            "connection_id": uuid4(),
            "name": "Test Account 1",
            "number": "123",
            "balance": 1000,
            "currency": "USD",
            "institution_name": "Test Broker"
        }
    ]

    await repo.upsert_accounts(accounts_data)

    # Check that execute and commit were called
    mock_session.execute.assert_called_once()
    mock_session.commit.assert_called_once()

    # Further inspection of the statement could be done here if needed,
    # but it would require more complex mocking of the insert statement itself.
    # For now, we trust that the SQLAlchemy statement is constructed correctly.

@pytest.mark.anyio
async def test_get_accounts_for_user():
    """
    Test that get_accounts returns accounts for a specific user.
    """
    mock_session = AsyncMock(spec=AsyncSession)
    repo = BrokerageAccountRepository(mock_session)
    user_id = uuid4()

    # Mock accounts should have all required fields from the model
    mock_accounts = [
        BrokerageAccount(id=uuid4(), user_id=user_id, connection_id=uuid4(), name="Account 1", number="1", balance=1, currency="USD", institution_name="Broker"),
        BrokerageAccount(id=uuid4(), user_id=user_id, connection_id=uuid4(), name="Account 2", number="2", balance=2, currency="USD", institution_name="Broker"),
    ]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_accounts
    mock_session.execute.return_value = mock_result

    result = await repo.get_accounts(user_id=user_id)

    assert len(result) == 2
    assert result[0].name == "Account 1"
    mock_session.execute.assert_called_once()


@pytest.mark.anyio
async def test_get_accounts_for_user_and_connection():
    """
    Test that get_accounts can filter by connection_id.
    """
    mock_session = AsyncMock(spec=AsyncSession)
    repo = BrokerageAccountRepository(mock_session)
    user_id = uuid4()
    connection_id = uuid4()

    mock_accounts = [
        BrokerageAccount(id=uuid4(), user_id=user_id, connection_id=connection_id, name="Account 1", number="1", balance=1, currency="USD", institution_name="Broker"),
    ]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_accounts
    mock_session.execute.return_value = mock_result

    result = await repo.get_accounts(user_id=user_id, connection_id=connection_id)

    assert len(result) == 1
    assert result[0].connection_id == connection_id
    mock_session.execute.assert_called_once()
