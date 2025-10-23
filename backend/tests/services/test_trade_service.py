import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from decimal import Decimal
from datetime import datetime

from fastapi import HTTPException

from app.Services.trade_service import TradeService
from app.Schemas.trade import TradeCreate, TradeUpdate, TradeRead

pytestmark = pytest.mark.anyio

@pytest.fixture
def mock_db_session():
    return AsyncMock()

@pytest.fixture
def mock_claims():
    return {"sub": str(uuid4())}

@pytest.fixture
def trade_service(mock_db_session):
    service = TradeService(db=mock_db_session)
    service.repo = AsyncMock()
    service.trade_repo = AsyncMock()
    service.trading_account_repo = AsyncMock()
    service.general_account_repo = AsyncMock()
    service.tag_repo = AsyncMock()
    service.mistake_repo = AsyncMock()
    service.playbook_repo = AsyncMock()
    service.news_impact_repo = AsyncMock()
    service.psychology_state_repo = AsyncMock()
    return service

async def test_validate_and_get_trading_account_not_found(trade_service: TradeService, mock_claims):
    trade_service.general_account_repo.get_by_user_id.return_value = None
    with pytest.raises(HTTPException) as excinfo:
        await trade_service._validate_and_get_trading_account(mock_claims, uuid4())
    assert excinfo.value.status_code == 404
    assert "General Account non trovato" in excinfo.value.detail

async def test_validate_and_get_trading_account_invalid(trade_service: TradeService, mock_claims):
    general_account = MagicMock()
    general_account.id = uuid4()
    trade_service.general_account_repo.get_by_user_id.return_value = general_account
    trade_service.trading_account_repo.get_by_id.return_value = None
    with pytest.raises(HTTPException) as excinfo:
        await trade_service._validate_and_get_trading_account(mock_claims, uuid4())
    assert excinfo.value.status_code == 404
    assert "Trading Account non valido o non appartenente all'utente" in excinfo.value.detail

def create_mock_trade(as_enum: bool = False):
    """
    Helper function to create a detailed mock Trade object for Pydantic validation.
    `as_enum` controls if the direction is a mock with a .value or a plain string.
    """
    trade = MagicMock()
    trade.id = uuid4()
    trade.symbol_snapshot = "AAPL"
    trade.direction = MagicMock(value="LONG") if as_enum else "LONG"
    trade.asset_id = uuid4()
    trade.trading_account_id = uuid4()
    trade.playbook = MagicMock(id=uuid4(), title="My Playbook")
    trade.tags = []
    trade.mistakes = []
    trade.news_impacts = []
    trade.psychology_states = []
    trade.rules_followed = []
    trade.entry_price = Decimal("150.0")
    trade.exit_price = Decimal("160.0")
    trade.stop_loss_price = Decimal("145.0")
    trade.take_profit_price = Decimal("165.0")
    trade.p_l = Decimal("10.0")
    trade.gross_p_l = Decimal("12.0")
    trade.fees = Decimal("1.0")
    trade.commissions = Decimal("1.0")
    trade.lowest_price_during_trade = Decimal("148.0")
    trade.highest_price_during_trade = Decimal("162.0")
    trade.position_size = Decimal("1.0")
    trade.r_multiple = 2.0
    trade.open_time = datetime.now()
    trade.close_time = datetime.now()
    trade.is_linked_to_note = False
    return trade

async def test_list_trades_by_trading_account_succeeds(trade_service: TradeService, mock_claims):
    trading_account_id = uuid4()
    general_account = MagicMock()
    general_account.id = uuid4()
    trading_account = MagicMock()
    trading_account.id = trading_account_id
    trading_account.general_account_id = general_account.id

    trade_service.general_account_repo.get_by_user_id.return_value = general_account
    trade_service.trading_account_repo.get_by_id.return_value = trading_account

    trades = [create_mock_trade(as_enum=False), create_mock_trade(as_enum=False)]
    trade_service.repo.list_by_trading_account_id.return_value = trades

    result = await trade_service.list_trades_by_trading_account(mock_claims, trading_account_id, None, None)

    assert result is not None
    assert len(result) == 2
    trade_service.repo.list_by_trading_account_id.assert_called_once_with(trading_account_id)

async def test_get_trade_succeeds(trade_service: TradeService, mock_claims):
    trade_id = uuid4()
    mock_trade = create_mock_trade(as_enum=False)
    mock_trade.id = trade_id

    general_account = MagicMock()
    general_account.id = uuid4()
    trading_account = MagicMock()
    trading_account.id = mock_trade.trading_account_id
    trading_account.general_account_id = general_account.id
    trading_account.initial_balance = "10000.0"

    trade_service.general_account_repo.get_by_user_id.return_value = general_account
    trade_service.trading_account_repo.get_by_id.return_value = trading_account
    trade_service.repo.get_trade_for_details_view.return_value = mock_trade

    result = await trade_service.get_trade(mock_claims, trade_id)

    assert result is not None
    trade_service.repo.get_trade_for_details_view.assert_called_once_with(trade_id)

async def test_get_trade_not_found(trade_service: TradeService, mock_claims):
    trade_id = uuid4()
    trade_service.repo.get_trade_for_details_view.return_value = None

    result = await trade_service.get_trade(mock_claims, trade_id)

    assert result is None

async def test_get_trade_not_authorized(trade_service: TradeService, mock_claims):
    trade_id = uuid4()
    user_general_account = MagicMock()
    user_general_account.id = uuid4()

    trade = MagicMock()
    trade.id = trade_id
    trade.trading_account_id = uuid4() # Different from any user account

    trade_service.repo.get_trade_for_details_view.return_value = trade
    trade_service.general_account_repo.get_by_user_id.return_value = user_general_account
    # This will now fail in _validate_and_get_trading_account
    trade_service.trading_account_repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        await trade_service.get_trade(mock_claims, trade_id)

    assert excinfo.value.status_code == 404
    assert "Trading Account non valido o non appartenente all'utente" in excinfo.value.detail

async def test_create_trade_succeeds(trade_service: TradeService, mock_claims, mocker):
    mocker.patch('app.Services.trading_account_service.TradingAccountService.recalculate_account_metrics', new_callable=AsyncMock)

    trade_create = TradeCreate(
        trading_account_id=uuid4(),
        asset_id=uuid4(),
        direction="LONG",
        entry_price=Decimal("100.0"),
        exit_price=Decimal("110.0"),
        stop_loss=Decimal("95.0"),
        take_profit=Decimal("115.0"),
        quantity=Decimal("1.0"),
        p_l=Decimal("10.0"),
        open_time=datetime.now(),
        close_time=datetime.now(),
        tags=[],
        mistakes=[],
        news_impacts=[],
        psychology_states=[]
    )

    general_account = MagicMock()
    general_account.id = uuid4()
    trading_account = MagicMock()
    trading_account.id = trade_create.trading_account_id
    trading_account.general_account_id = general_account.id
    trading_account.initial_balance = "10000.0"

    trade_service.general_account_repo.get_by_user_id.return_value = general_account
    trade_service.trading_account_repo.get_by_id.return_value = trading_account
    trade_service.db.add = MagicMock()
    trade_service.db.commit = AsyncMock()

    async def mock_refresh(obj, *args, **kwargs):
        obj.id = uuid4()
        obj.created_at = datetime.now()

    trade_service.db.refresh = AsyncMock(side_effect=mock_refresh)

    result = await trade_service.create_trade(mock_claims, trade_create)

    assert result is not None
    assert result.id is not None
    trade_service.db.add.assert_called_once()
    trade_service.db.commit.assert_called_once()

async def test_update_trade_succeeds(trade_service: TradeService, mock_claims, mocker):
    mocker.patch('app.Services.trading_account_service.TradingAccountService.recalculate_account_metrics', new_callable=AsyncMock)

    trade_id = uuid4()
    trade_update = TradeUpdate(
        direction="SHORT",
        p_l=Decimal("-5.0")
    )

    general_account = MagicMock()
    general_account.id = uuid4()
    trading_account = MagicMock()
    trading_account.id = uuid4()
    trading_account.general_account_id = general_account.id
    trading_account.initial_balance = "10000.0"

    db_trade = create_mock_trade(as_enum=True)
    db_trade.id = trade_id
    db_trade.trading_account_id = trading_account.id

    trade_service.repo.get_trade_by_id_simple.return_value = db_trade
    trade_service.general_account_repo.get_by_user_id.return_value = general_account
    trade_service.trading_account_repo.get_by_id.return_value = trading_account
    trade_service.db.commit = AsyncMock()
    trade_service.db.refresh = AsyncMock()

    result = await trade_service.update_trade(mock_claims, trade_id, trade_update)

    assert result is not None
    trade_service.repo.get_trade_by_id_simple.assert_called_once_with(trade_id)
    trade_service.db.commit.assert_called_once()

async def test_update_trade_not_found(trade_service: TradeService, mock_claims):
    trade_id = uuid4()
    trade_update = TradeUpdate()

    trade_service.repo.get_trade_by_id_simple.return_value = None

    result = await trade_service.update_trade(mock_claims, trade_id, trade_update)

    assert result is None

async def test_delete_trade_succeeds(trade_service: TradeService, mock_claims, mocker):
    mocker.patch('app.Services.trading_account_service.TradingAccountService.recalculate_account_metrics', new_callable=AsyncMock)
    trade_id = uuid4()

    general_account = MagicMock()
    general_account.id = uuid4()
    trading_account = MagicMock()
    trading_account.id = uuid4()
    trading_account.general_account_id = general_account.id

    trade = MagicMock()
    trade.id = trade_id
    trade.trading_account_id = trading_account.id

    trade_service.repo.get_trade_by_id_simple.return_value = trade
    trade_service.general_account_repo.get_by_user_id.return_value = general_account
    trade_service.trading_account_repo.get_by_id.return_value = trading_account
    trade_service.repo.delete_trade = AsyncMock()

    result = await trade_service.delete_trade(mock_claims, trade_id)

    assert result is True
    trade_service.repo.delete_trade.assert_called_once_with(trade)

async def test_delete_trade_not_found(trade_service: TradeService, mock_claims):
    trade_id = uuid4()

    trade_service.repo.get_trade_by_id_simple.return_value = None

    result = await trade_service.delete_trade(mock_claims, trade_id)

    assert result is False

async def test_update_trade_rules_succeeds(trade_service: TradeService, mock_claims):
    trade_id = uuid4()
    rule_ids = [uuid4(), uuid4()]

    general_account = MagicMock()
    general_account.id = uuid4()
    trading_account = MagicMock()
    trading_account.id = uuid4()
    trading_account.general_account_id = general_account.id

    db_trade = create_mock_trade(as_enum=True)
    db_trade.id = trade_id
    db_trade.trading_account_id = trading_account.id

    trade_service.repo.get_trade_by_id_simple.return_value = db_trade
    trade_service.general_account_repo.get_by_user_id.return_value = general_account
    trade_service.trading_account_repo.get_by_id.return_value = trading_account

    # Mock the database execution for fetching rules
    mock_rule_1 = MagicMock()
    mock_rule_1.id = rule_ids[0]
    mock_rule_2 = MagicMock()
    mock_rule_2.id = rule_ids[1]
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_rule_1, mock_rule_2]
    trade_service.db.execute = AsyncMock(return_value=mock_result)

    trade_service.db.commit = AsyncMock()
    # When refresh is called, update the rules_followed attribute
    async def mock_refresh(trade, attribute_names):
        trade.rules_followed = [mock_rule_1, mock_rule_2]
    trade_service.db.refresh = AsyncMock(side_effect=mock_refresh)


    result = await trade_service.update_trade_rules(mock_claims, trade_id, rule_ids)

    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(item, type(uuid4())) for item in result)
    assert set(result) == set(rule_ids)
    trade_service.db.commit.assert_called_once()
    trade_service.db.refresh.assert_called_once_with(db_trade, attribute_names=['rules_followed'])