import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import uuid4
from fastapi import status

from app.main import app
from app.Models.asset import Asset
from app.Models.asset_class import AssetClass
from app.Models.asset_market import AssetMarket
from app.Models.broker import Broker
from app.Models.role import Role
from app.Models.auth_user import AuthUser
from app.Models.user_role import UserRole
from app.Models.general_account import GeneralAccount
from app.Models.mistake import Mistake
from app.Models.news_impact import NewsImpact
from app.Models.psychology_state import PsychologyState
from app.Models.tags_group import TagsGroup
from app.Models.tag import Tag
from app.Models.enums import TradeDirection
from app.Models.playbook import Playbook
from app.Models.trade import Trade
from app.Models.trading_account import TradingAccount
from app.Router.auth import get_current_claims

@pytest.fixture(scope="module")
def anyio_backend():
    """Use asyncio for all tests in this module."""
    return "asyncio"

@pytest.fixture
async def admin_user(db_session: AsyncSession) -> AuthUser:
    """Creates an admin user, ensuring the 'admin' role exists."""
    stmt = select(Role).where(Role.name == "admin")
    result = await db_session.execute(stmt)
    admin_role = result.scalars().first()
    if not admin_role:
        admin_role = Role(id=uuid4(), name="admin", description="Administrator")
        db_session.add(admin_role)
        await db_session.flush()

    user = AuthUser(id=uuid4(), email=f"admin_{uuid4()}@test.com")
    db_session.add(user)
    await db_session.flush()

    user_role = UserRole(user_id=user.id, role_id=admin_role.id)
    db_session.add(user_role)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
async def regular_user(db_session: AsyncSession) -> AuthUser:
    """Creates a regular user for testing."""
    user = AuthUser(id=uuid4(), email=f"user_{uuid4()}@test.com")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
def admin_client(async_client: AsyncClient, admin_user: AuthUser) -> AsyncClient:
    """Provides a test client authenticated as an admin user."""
    app.dependency_overrides[get_current_claims] = lambda: {
        "sub": str(admin_user.id),
        "email": admin_user.email,
    }
    return async_client

@pytest.fixture
def user_client(async_client: AsyncClient, regular_user: AuthUser) -> AsyncClient:
    """Provides a test client authenticated as a regular user."""
    app.dependency_overrides[get_current_claims] = lambda: {
        "sub": str(regular_user.id),
        "email": regular_user.email,
    }
    return async_client

@pytest.fixture
async def test_broker(db_session: AsyncSession) -> Broker:
    """Fixture for a pre-existing broker."""
    broker = Broker(name=f"Test Broker Inc. {uuid4()}")
    db_session.add(broker)
    await db_session.commit()
    await db_session.refresh(broker)
    return broker

@pytest.fixture
async def general_account_with_data(
    db_session: AsyncSession, regular_user: AuthUser, test_broker: Broker
) -> GeneralAccount:
    """
    Crea un GeneralAccount per l'utente e lo popola con dati correlati
    (mistakes, news, psychology, tags, trading accounts, trades) per testare l'endpoint "with-data".
    """
    # Crea il GeneralAccount
    general_account = GeneralAccount(user_id=regular_user.id, label=regular_user.email)
    db_session.add(general_account)
    await db_session.flush()

    # Crea dati correlati e associali
    mistake = Mistake(name="Test Mistake", general_account_id=general_account.id)
    news_impact = NewsImpact(name="Test News", general_account_id=general_account.id)
    psychology_state = PsychologyState(
        name="Test State", general_account_id=general_account.id
    )
    tags_group = TagsGroup(name="Test Group", general_account_id=general_account.id)
    playbook = Playbook(
        title="Test Playbook",
        description="Test playbook description",
        general_account_id=general_account.id,
    )
    db_session.add_all([mistake, news_impact, psychology_state, tags_group, playbook])
    await db_session.flush()

    # Crea tag per il gruppo
    tag1 = Tag(name="Tag 1", group_id=tags_group.id, color="#FF0000")
    tag2 = Tag(name="Tag 2", group_id=tags_group.id, color="#00FF00")
    db_session.add_all([tag1, tag2])
    await db_session.flush()

    # Crea asset e i suoi prerequisiti (se non esistono)
    stmt_ac = select(AssetClass).where(AssetClass.name == "Futures")
    asset_class = (await db_session.execute(stmt_ac)).scalars().first()
    if not asset_class:
        asset_class = AssetClass(name="Futures")
        db_session.add(asset_class)
        await db_session.flush()

    stmt_am = select(AssetMarket).where(AssetMarket.name == "CME")
    asset_market = (await db_session.execute(stmt_am)).scalars().first()
    if not asset_market:
        asset_market = AssetMarket(name="CME")
        db_session.add(asset_market)
        await db_session.flush()

    asset = Asset(
        symbol="ES",
        name="E-mini S&P 500",
        asset_class_id=asset_class.id,
        asset_market_id=asset_market.id,
    )
    db_session.add(asset)
    await db_session.flush()

    # Crea TradingAccount
    trading_account = TradingAccount(
        general_account_id=general_account.id,
        broker_id=test_broker.id,
        label="Test Trading Account",
        initial_balance=10000,
        currency="USD",
    )
    db_session.add(trading_account)
    await db_session.flush()

    # Crea Trade e associalo
    trade = Trade(
        trading_account_id=trading_account.id,
        asset_id=asset.id,
        p_l=150.75,
        direction=TradeDirection.LONG,
        playbook_id=playbook.id,
    )
    trade.mistakes.append(mistake)
    trade.tags.append(tag1)
    db_session.add(trade)

    await db_session.commit()
    await db_session.refresh(general_account)

    return general_account