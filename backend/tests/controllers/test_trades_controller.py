import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from decimal import Decimal
from datetime import datetime, timezone, date
from uuid import uuid4
from fastapi import HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

# Importa l'app FastAPI e le dipendenze da mockare
from app.main import app
from app.Models.trade import Trade, TradeDirectionEnum
from app.Repositories.trade_repository import TradeRepository
from app.Infrastructure.db import get_db
from app.Router.auth import get_current_claims
from app.Controllers.trades_controller import TradesController
from app.Schemas.trade import TradeCreate, TradeUpdate
from app.Schemas.vantage_score import VantageScoreData
from app.Schemas.stats import EquityCurveData, TradeSummary, ProcessedStats, SummaryStats

# ------------------------------
# Fixtures for New Unit Tests
# ------------------------------

@pytest.fixture
def trades_controller():
    """Returns an instance of the TradesController."""
    return TradesController()

@pytest.fixture
def mock_db_session():
    """Provides a mock AsyncSession."""
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def mock_trade_repo(mocker):
    """Mocks the TradeRepository."""
    return mocker.patch("app.Controllers.trades_controller.TradeRepository")

# Mock data
mock_user_id = uuid4()
utc_entry_time = datetime(2023, 10, 26, 23, 30, 0, tzinfo=timezone.utc)
mock_trade_orm = Trade(
    id=uuid4(),
    user_id=mock_user_id,
    p_l=Decimal("150.00"),
    entry_timestamp=utc_entry_time,
    exit_timestamp=utc_entry_time,
    created_at=utc_entry_time,
    setup="Test Setup",
    symbol="EURUSD",
    direction=TradeDirectionEnum.Long,
    entry_price=Decimal("1.1000"),
    exit_price=Decimal("1.1150"),
    stop_loss_price=Decimal("1.0950")
)

# ------------------------------
# New Unit Tests
# ------------------------------

@pytest.mark.anyio
async def test_list_trades_with_filters(trades_controller: TradesController, mock_db_session: AsyncSession, mock_trade_repo):
    """Test list_trades calls repository with correct filters."""
    mock_trade_repo.return_value.list_with_filters = AsyncMock(return_value=[(mock_trade_orm, ["tag1"])])

    await trades_controller.list_trades(
        user_id=mock_user_id,
        symbol="EURUSD",
        db=mock_db_session
    )

    mock_trade_repo.return_value.list_with_filters.assert_called_once()
    call_kwargs = mock_trade_repo.return_value.list_with_filters.call_args.kwargs
    assert call_kwargs['user_id'] == mock_user_id
    assert call_kwargs['symbol'] == "EURUSD"

@pytest.mark.anyio
async def test_get_trade_success(trades_controller: TradesController, mock_db_session: AsyncSession, mock_trade_repo):
    """Test successful retrieval of a single trade."""
    trade_id = mock_trade_orm.id
    mock_trade_repo.return_value.get_by_id_with_tags = AsyncMock(return_value=(mock_trade_orm, ["tag1"]))

    response = await trades_controller.get_trade(trade_id, mock_user_id, mock_db_session)

    assert response.id == trade_id
    assert response.symbol == "EURUSD"
    mock_trade_repo.return_value.get_by_id_with_tags.assert_called_once_with(mock_user_id, trade_id)

@pytest.mark.anyio
async def test_get_trade_not_found(trades_controller: TradesController, mock_db_session: AsyncSession, mock_trade_repo):
    """Test get_trade for a non-existent trade."""
    trade_id = uuid4()
    mock_trade_repo.return_value.get_by_id_with_tags = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc_info:
        await trades_controller.get_trade(trade_id, mock_user_id, mock_db_session)

    assert exc_info.value.status_code == 404

@pytest.mark.anyio
async def test_create_trade_success(trades_controller: TradesController, mock_db_session: AsyncSession, mock_trade_repo):
    """Test successful creation of a trade."""
    payload = TradeCreate(symbol="GBPUSD", direction=TradeDirectionEnum.Short, tags=["new_tag"])
    mock_trade_repo.return_value.create_with_tags = AsyncMock(return_value=mock_trade_orm)
    mock_trade_repo.return_value.get_by_id_with_tags = AsyncMock(return_value=(mock_trade_orm, ["new_tag"]))

    response = await trades_controller.create_trade(payload, mock_user_id, mock_db_session)

    assert response.id == mock_trade_orm.id
    mock_trade_repo.return_value.create_with_tags.assert_called_once()

@pytest.mark.anyio
async def test_update_trade_success(trades_controller: TradesController, mock_db_session: AsyncSession, mock_trade_repo):
    """Test successful update of a trade."""
    trade_id = mock_trade_orm.id
    payload = TradeUpdate(notes="Updated notes.")
    mock_trade_repo.return_value.update_with_tags = AsyncMock(return_value=mock_trade_orm)
    mock_trade_repo.return_value.get_by_id_with_tags = AsyncMock(return_value=(mock_trade_orm, []))

    response = await trades_controller.update_trade(trade_id, payload, mock_user_id, mock_db_session)

    assert response.id == trade_id
    mock_trade_repo.return_value.update_with_tags.assert_called_once()

@pytest.mark.anyio
async def test_update_trade_not_found(trades_controller: TradesController, mock_db_session: AsyncSession, mock_trade_repo):
    """Test updating a non-existent trade."""
    trade_id = uuid4()
    payload = TradeUpdate(notes="Updated notes.")
    mock_trade_repo.return_value.update_with_tags = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc_info:
        await trades_controller.update_trade(trade_id, payload, mock_user_id, mock_db_session)

    assert exc_info.value.status_code == 404

@pytest.mark.anyio
async def test_delete_trade_success(trades_controller: TradesController, mock_db_session: AsyncSession, mock_trade_repo):
    """Test successful deletion of a trade."""
    trade_id = uuid4()
    mock_trade_repo.return_value.delete = AsyncMock(return_value=True)

    response = await trades_controller.delete_trade(trade_id, mock_user_id, mock_db_session)

    assert isinstance(response, Response)
    assert response.status_code == 204
    mock_trade_repo.return_value.delete.assert_called_once_with(mock_user_id, trade_id)

@pytest.mark.anyio
async def test_delete_trade_not_found(trades_controller: TradesController, mock_db_session: AsyncSession, mock_trade_repo):
    """Test deleting a non-existent trade."""
    trade_id = uuid4()
    mock_trade_repo.return_value.delete = AsyncMock(return_value=False)

    with pytest.raises(HTTPException) as exc_info:
        await trades_controller.delete_trade(trade_id, mock_user_id, mock_db_session)

    assert exc_info.value.status_code == 404

# ------------------------------
# New Statistics / Analytics Tests
# ------------------------------

@pytest.mark.anyio
async def test_list_setups(trades_controller: TradesController, mock_db_session: AsyncSession, mock_trade_repo):
    """Test listing unique setups."""
    mock_setups = ["Setup A", "Setup B"]
    mock_trade_repo.return_value.get_distinct_setups = AsyncMock(return_value=mock_setups)

    response = await trades_controller.list_setups(mock_user_id, mock_db_session)

    assert response == mock_setups
    mock_trade_repo.return_value.get_distinct_setups.assert_called_once_with(mock_user_id)

@pytest.mark.anyio
async def test_calendar_data(trades_controller: TradesController, mock_db_session: AsyncSession, mock_trade_repo):
    """Test retrieving calendar data."""
    mock_calendar = [{"date": "2023-01-01", "pnl": 100.0}]
    mock_trade_repo.return_value.get_calendar_data = AsyncMock(return_value=mock_calendar)

    response = await trades_controller.calendar_data(user_id=mock_user_id, db=mock_db_session)

    assert response == mock_calendar
    mock_trade_repo.return_value.get_calendar_data.assert_called_once()

@pytest.mark.anyio
async def test_get_performance_metrics(trades_controller: TradesController, mock_db_session: AsyncSession, mock_trade_repo, mocker):
    """Test retrieving performance metrics."""
    mock_trade_repo.return_value.list_with_filters = AsyncMock(return_value=[(mock_trade_orm, ["tag1"])])
    mock_calculator = mocker.patch("app.Controllers.trades_controller.MetricsCalculator")
    mock_calculator.return_value.calculate_all_metrics.return_value = {"win_rate": 0.5}

    response = await trades_controller.get_performance_metrics(user_id=mock_user_id, db=mock_db_session)

    assert response["win_rate"] == 0.5
    mock_calculator.assert_called_once()
    mock_calculator.return_value.calculate_all_metrics.assert_called_once()

@pytest.mark.anyio
async def test_get_vantage_score(trades_controller: TradesController, mock_db_session: AsyncSession, mock_trade_repo, mocker):
    """Test retrieving vantage score."""
    mock_trade_repo.return_value.list_with_filters = AsyncMock(return_value=[(mock_trade_orm, ["tag1"])])
    mock_calculator = mocker.patch("app.Controllers.trades_controller.MetricsCalculator")
    mock_calculator.return_value.calculate_vantage_score.return_value = VantageScoreData(
        vantage_score=80.0,
        profit_factor_score=80.0,
        avg_win_loss_score=80.0,
        max_drawdown_score=80.0,
        win_rate_score=80.0,
        consistency_score=80.0,
        recovery_factor_score=80.0
    ).model_dump()

    response = await trades_controller.get_vantage_score(user_id=mock_user_id, db=mock_db_session)

    assert response.vantage_score == 80.0
    mock_calculator.assert_called_once()
    mock_calculator.return_value.calculate_vantage_score.assert_called_once()

@pytest.mark.anyio
async def test_get_equity_curve(trades_controller: TradesController, mock_db_session: AsyncSession, mock_trade_repo, mocker):
    """Test retrieving equity curve data."""
    mock_trade_repo.return_value.list_with_filters = AsyncMock(return_value=[(mock_trade_orm, ["tag1"])])
    mock_calculator = mocker.patch("app.Controllers.trades_controller.MetricsCalculator")
    mock_calculator.return_value.calculate_equity_curve.return_value = EquityCurveData(
        labels=["2023-01-01"],
        data=[10150.0]
    ).model_dump()

    response = await trades_controller.get_equity_curve(user_id=mock_user_id, db=mock_db_session)

    assert response.labels == ["2023-01-01"]
    assert response.data == [10150.0]
    mock_calculator.assert_called_once()
    mock_calculator.return_value.calculate_equity_curve.assert_called_once()

@pytest.mark.anyio
async def test_get_trade_summary(trades_controller: TradesController, mock_db_session: AsyncSession, mock_trade_repo, mocker):
    """Test retrieving trade summary."""
    mock_trade_repo.return_value.list_with_filters = AsyncMock(return_value=[(mock_trade_orm, ["tag1"])])
    mock_calculator = mocker.patch("app.Controllers.trades_controller.MetricsCalculator")

    summary_stats = SummaryStats(
        net_pnl=150.0,
        trade_count=1,
        winning_trades=1,
        losing_trades=0,
        breakeven_trades=0,
        gross_profit=150.0,
        gross_loss=0.0,
        profit_factor=None,
        win_rate=100.0
    )
    equity_curve = EquityCurveData(labels=["2023-10-27"], data=[150.0])

    mock_calculator.return_value.calculate_trade_summary.return_value = TradeSummary(
        stats=summary_stats,
        cumulative_pnl_series=equity_curve
    ).model_dump()

    response = await trades_controller.get_trade_summary(user_id=mock_user_id, db=mock_db_session)

    assert response.stats.net_pnl == 150.0
    assert response.stats.trade_count == 1
    mock_calculator.assert_called_once()
    mock_calculator.return_value.calculate_trade_summary.assert_called_once()

# ------------------------------
# Existing Integration Test (kept as is)
# ------------------------------

@pytest.fixture
def test_client():
    """
    Crea un client di test per l'app FastAPI, sovrascrivendo le dipendenze
    del database e dell'autenticazione per isolare il test.
    """
    async def override_get_db():
        yield None

    async def override_get_current_claims():
        return {"sub": str(mock_user_id), "roles": ["member"]}

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_claims] = override_get_current_claims

    original_list_with_filters = TradeRepository.list_with_filters
    TradeRepository.list_with_filters = AsyncMock(return_value=[(mock_trade_orm, [])])

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
    TradeRepository.list_with_filters = original_list_with_filters

def test_get_processed_stats_with_timezone(test_client):
    """
    Test di integrazione per l'endpoint /api/v1/trades/processed-stats
    """
    user_timezone = "Europe/Rome"
    expected_local_date = "2023-10-27"

    response = test_client.get(
        f"/api/v1/trades/processed-stats?user_id={mock_user_id}&user_timezone={user_timezone}"
    )

    assert response.status_code == 200
    data = response.json()
    assert "daily_data" in data
    assert expected_local_date in data["daily_data"]
    assert "2023-10-26" not in data["daily_data"]
    day_stats = data["daily_data"][expected_local_date]
    assert day_stats["total_pnl"] == float(mock_trade_orm.p_l)
    assert day_stats["trade_count"] == 1
    assert day_stats["winning_trades"] == 1
