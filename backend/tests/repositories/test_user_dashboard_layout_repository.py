import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.Repositories.user_dashboard_layout_repository import UserDashboardLayoutRepository
from app.Models.user_dashboard_layout import UserDashboardLayout
from app.Models.auth_user import AuthUser
from app.Schemas.user_dashboard_layout import UserDashboardLayoutCreate, UserDashboardLayoutUpdate, ZonedLayout, WidgetItem

pytestmark = pytest.mark.anyio

@pytest.fixture
async def setup_user(db_session: AsyncSession):
    """Fixture to create a user."""
    user = AuthUser(id=uuid4(), email="layout.user@test.com")
    db_session.add(user)
    await db_session.commit()
    return user

@pytest.fixture
def layout_repo(db_session: AsyncSession) -> UserDashboardLayoutRepository:
    return UserDashboardLayoutRepository(db_session)

@pytest.fixture
def sample_layout_data() -> ZonedLayout:
    """Returns a sample layout structure."""
    return ZonedLayout(
        stats=[WidgetItem(i="a", x=0, y=0, w=1, h=1)],
        main=[WidgetItem(i="b", x=1, y=0, w=3, h=2)],
        charts=[WidgetItem(i="c", x=4, y=0, w=2, h=2)]
    )

async def test_create_layout_raises_on_duplicate_user_id(
    layout_repo: UserDashboardLayoutRepository,
    setup_user: AuthUser,
    sample_layout_data: ZonedLayout
):
    """Test that creating a layout for a user who already has one raises an exception."""
    user_id = setup_user.id

    # Create the first layout
    layout_create_1 = UserDashboardLayoutCreate(user_id=user_id, layout=sample_layout_data)
    await layout_repo.create(layout_create_1)

    # Try to create a second layout for the same user
    layout_create_2 = UserDashboardLayoutCreate(user_id=user_id, layout=sample_layout_data)
    with pytest.raises(HTTPException) as exc_info:
        await layout_repo.create(layout_create_2)

    assert exc_info.value.status_code == 409
    assert "already exists" in exc_info.value.detail

async def test_update_layout(
    layout_repo: UserDashboardLayoutRepository,
    db_session: AsyncSession,
    setup_user: AuthUser,
    sample_layout_data: ZonedLayout
):
    """Test updating an existing layout."""
    user_id = setup_user.id

    # Create an initial layout
    initial_layout = UserDashboardLayout(user_id=user_id, layout=sample_layout_data.model_dump())
    db_session.add(initial_layout)
    await db_session.commit()

    # New layout data for the update
    new_layout_config = ZonedLayout(
        stats=[WidgetItem(i="new_a", x=0, y=0, w=1, h=1)],
        main=[],
        charts=[]
    )
    update_schema = UserDashboardLayoutUpdate(layout=new_layout_config)

    updated_layout = await layout_repo.update(initial_layout, update_schema)

    assert updated_layout is not None
    # Pydantic v2 models store dicts, not model instances
    assert updated_layout.layout["stats"][0]["i"] == "new_a"