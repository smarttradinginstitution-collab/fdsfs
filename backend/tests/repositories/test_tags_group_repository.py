import pytest
from uuid import uuid4
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.Repositories.tags_group_repository import TagsGroupRepository
from app.Models.tags_group import TagsGroup
from app.Models.general_account import GeneralAccount
from app.Schemas.tags_group import TagsGroupCreate, TagsGroupUpdate

pytestmark = pytest.mark.anyio

@pytest.fixture
async def general_account(db_session: AsyncSession) -> GeneralAccount:
    """Fixture to create a general account."""
    user_id = uuid4()
    account = GeneralAccount(id=uuid4(), user_id=user_id, label="test_account")
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account

async def test_create_and_get_tags_group(db_session: AsyncSession, general_account: GeneralAccount):
    """Test creating and retrieving a tags group."""
    repo = TagsGroupRepository(db_session)
    tags_group_data = TagsGroupCreate(name="Test Group", description="A test group")

    created_group = await repo.create_tags_group(tags_group_data, general_account.id)

    assert created_group.id is not None
    assert created_group.name == "Test Group"
    assert created_group.general_account_id == general_account.id

    retrieved_group = await repo.get_tags_group_by_id(created_group.id, general_account.id)

    assert retrieved_group is not None
    assert retrieved_group.id == created_group.id
    assert retrieved_group.name == "Test Group"

async def test_update_tags_group(db_session: AsyncSession, general_account: GeneralAccount):
    """Test updating a tags group."""
    repo = TagsGroupRepository(db_session)
    tags_group = TagsGroup(name="Original Name", general_account_id=general_account.id)
    db_session.add(tags_group)
    await db_session.commit()

    update_data = TagsGroupUpdate(name="Updated Name")
    updated_group = await repo.update_tags_group(tags_group, update_data)

    assert updated_group.name == "Updated Name"

async def test_list_tags_groups(db_session: AsyncSession, general_account: GeneralAccount):
    """Test listing tags groups for a general account."""
    repo = TagsGroupRepository(db_session)

    # Create some groups
    group1 = TagsGroup(name="Group 1", general_account_id=general_account.id)
    group2 = TagsGroup(name="Group 2", general_account_id=general_account.id)
    db_session.add_all([group1, group2])
    await db_session.commit()

    groups = await repo.list_tags_groups_by_general_account_id(general_account.id)

    assert len(groups) == 2
    assert {group.name for group in groups} == {"Group 1", "Group 2"}

async def test_delete_tags_group(db_session: AsyncSession, general_account: GeneralAccount):
    """Test deleting a tags group."""
    repo = TagsGroupRepository(db_session)
    tags_group = TagsGroup(name="To Be Deleted", general_account_id=general_account.id)
    db_session.add(tags_group)
    await db_session.commit()

    group_id = tags_group.id

    await repo.delete_tags_group(tags_group)

    deleted_group = await repo.get_tags_group_by_id(group_id, general_account.id)
    assert deleted_group is None

async def test_create_duplicate_tags_group_raises_exception(db_session: AsyncSession, general_account: GeneralAccount):
    """Test that creating a tags group with a duplicate name raises an exception."""
    repo = TagsGroupRepository(db_session)
    tags_group_data = TagsGroupCreate(name="Duplicate Group")

    # Create the first group
    await repo.create_tags_group(tags_group_data, general_account.id)

    # Attempt to create a second group with the same name
    with pytest.raises(HTTPException) as excinfo:
        await repo.create_tags_group(tags_group_data, general_account.id)

    assert excinfo.value.status_code == 409

async def test_create_duplicate_tags_group_case_insensitive(db_session: AsyncSession, general_account: GeneralAccount):
    """Test that duplicate check is case-insensitive."""
    repo = TagsGroupRepository(db_session)

    # Create the first group
    await repo.create_tags_group(TagsGroupCreate(name="Unique Name"), general_account.id)

    # Attempt to create a group with the same name but different case
    with pytest.raises(HTTPException) as excinfo:
        await repo.create_tags_group(TagsGroupCreate(name="unique name"), general_account.id)

    assert excinfo.value.status_code == 409