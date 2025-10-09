import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.Repositories.role_repository import RoleRepository
from app.Models.role import Role
from app.Schemas.role import RoleCreate, RoleUpdate

pytestmark = pytest.mark.anyio

@pytest.fixture
def role_repo(db_session: AsyncSession) -> RoleRepository:
    return RoleRepository(db_session)

async def test_create_role(role_repo: RoleRepository):
    """Test creating a new role."""
    role_create = RoleCreate(name="Admin", description="Administrator role")
    created_role = await role_repo.create(role_create.model_dump())
    assert created_role is not None
    assert created_role.name == "Admin"
    assert created_role.id is not None

async def test_create_role_raises_on_duplicate_name(
    role_repo: RoleRepository,
):
    """Test that creating a role with a duplicate name raises an exception."""
    role_create = RoleCreate(name="Moderator")
    await role_repo.create(role_create.model_dump())

    with pytest.raises(HTTPException) as exc_info:
        await role_repo.create(role_create.model_dump())

    assert exc_info.value.status_code == 409
    assert "already exists" in exc_info.value.detail

async def test_update_role(
    role_repo: RoleRepository, db_session: AsyncSession
):
    """Test updating a role's name."""
    role = Role(name="Old Role", description="...")
    db_session.add(role)
    await db_session.commit()

    update_schema = RoleUpdate(name="New Role")
    updated_role = await role_repo.update(role.id, update_schema.model_dump())

    assert updated_role is not None
    assert updated_role.name == "New Role"

async def test_update_role_raises_on_duplicate_name(
    role_repo: RoleRepository, db_session: AsyncSession
):
    """Test that updating a role to a duplicate name raises an exception."""
    role1 = Role(name="Role A")
    role2 = Role(name="Role B")
    db_session.add_all([role1, role2])
    await db_session.commit()

    update_schema = RoleUpdate(name="Role A")
    with pytest.raises(HTTPException) as exc_info:
        await role_repo.update(role2.id, update_schema.model_dump())

    assert exc_info.value.status_code == 409
    assert "already exists" in exc_info.value.detail