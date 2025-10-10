import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.Repositories.platform_repository import PlatformRepository
from app.Models.platform import Platform
from app.Schemas.platform import PlatformCreate, PlatformUpdate

pytestmark = pytest.mark.anyio

@pytest.fixture
def platform_repo(db_session: AsyncSession) -> PlatformRepository:
    return PlatformRepository(db_session)

async def test_create_platform(platform_repo: PlatformRepository):
    """Test creating a new platform."""
    platform_create = PlatformCreate(name="MetaTrader 5")
    created_platform = await platform_repo.create(platform_create)
    assert created_platform is not None
    assert created_platform.name == "MetaTrader 5"
    assert created_platform.id is not None

async def test_create_platform_raises_on_duplicate_name(
    platform_repo: PlatformRepository,
):
    """Test that creating a platform with a duplicate name raises an exception."""
    platform_create = PlatformCreate(name="TradingView")
    await platform_repo.create(platform_create)

    with pytest.raises(HTTPException) as exc_info:
        await platform_repo.create(platform_create)

    assert exc_info.value.status_code == 409
    assert "already exists" in exc_info.value.detail

async def test_update_platform(
    platform_repo: PlatformRepository, db_session: AsyncSession
):
    """Test updating a platform's name."""
    platform = Platform(name="Old Platform")
    db_session.add(platform)
    await db_session.commit()

    update_schema = PlatformUpdate(name="New Platform")
    updated_platform = await platform_repo.update(platform, update_schema)

    assert updated_platform is not None
    assert updated_platform.name == "New Platform"

async def test_update_platform_raises_on_duplicate_name(
    platform_repo: PlatformRepository, db_session: AsyncSession
):
    """Test that updating a platform to a duplicate name raises an exception."""
    platform1 = Platform(name="Platform A")
    platform2 = Platform(name="Platform B")
    db_session.add_all([platform1, platform2])
    await db_session.commit()

    update_schema = PlatformUpdate(name="Platform A")
    with pytest.raises(HTTPException) as exc_info:
        await platform_repo.update(platform2, update_schema)

    assert exc_info.value.status_code == 409
    assert "already exists" in exc_info.value.detail