import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.Controllers.roles_controller import RolesController
from app.Schemas.role import RoleCreate, RoleUpdate
from app.Models.role import Role

# ------------------------------
# Fixtures
# ------------------------------

@pytest.fixture
def roles_controller():
    """Returns an instance of the RolesController."""
    return RolesController()

@pytest.fixture
def mock_db_session():
    """Provides a mock AsyncSession."""
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def mock_role_service(mocker):
    """Mocks the RoleService."""
    return mocker.patch("app.Controllers.roles_controller.RoleService")

# ------------------------------
# list_roles Tests
# ------------------------------

@pytest.mark.anyio
async def test_list_roles_success(roles_controller: RolesController, mock_db_session: AsyncSession, mock_role_service):
    """Test successful retrieval of all roles."""
    role_id = uuid4()
    mock_roles = [Role(id=role_id, name="admin", description="Administrator")]
    mock_role_service.return_value.roles.list = AsyncMock(return_value=mock_roles)

    response = await roles_controller.list_roles(mock_db_session)

    assert len(response) == 1
    assert response[0].id == role_id
    assert response[0].name == "admin"
    mock_role_service.return_value.roles.list.assert_called_once()

# ------------------------------
# get_role Tests
# ------------------------------

@pytest.mark.anyio
async def test_get_role_success(roles_controller: RolesController, mock_db_session: AsyncSession, mock_role_service):
    """Test successful retrieval of a single role."""
    role_id = uuid4()
    mock_role = Role(id=role_id, name="user", description="User role")
    mock_role_service.return_value.roles.get = AsyncMock(return_value=mock_role)

    response = await roles_controller.get_role(role_id, mock_db_session)

    assert response.id == role_id
    assert response.name == "user"
    mock_role_service.return_value.roles.get.assert_called_once_with(role_id)

@pytest.mark.anyio
async def test_get_role_not_found(roles_controller: RolesController, mock_db_session: AsyncSession, mock_role_service):
    """Test retrieval of a non-existent role."""
    role_id = uuid4()
    mock_role_service.return_value.roles.get = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc_info:
        await roles_controller.get_role(role_id, mock_db_session)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Ruolo non trovato" in exc_info.value.detail

# ------------------------------
# create_role Tests
# ------------------------------

@pytest.mark.anyio
async def test_create_role_success(roles_controller: RolesController, mock_db_session: AsyncSession, mock_role_service):
    """Test successful creation of a new role."""
    role_id = uuid4()
    payload = RoleCreate(name="moderator", description="Moderator role")
    mock_created_role = Role(id=role_id, **payload.model_dump())
    mock_role_service.return_value.roles.create = AsyncMock(return_value=mock_created_role)

    response = await roles_controller.create_role(payload, mock_db_session)

    assert response.id == role_id
    assert response.name == "moderator"
    mock_role_service.return_value.roles.create.assert_called_once_with(payload.model_dump())

# ------------------------------
# update_role Tests
# ------------------------------

@pytest.mark.anyio
async def test_update_role_success(roles_controller: RolesController, mock_db_session: AsyncSession, mock_role_service):
    """Test successful update of an existing role."""
    role_id = uuid4()
    payload = RoleUpdate(description="A new description")
    mock_updated_role = Role(id=role_id, name="editor", description="A new description")
    mock_role_service.return_value.roles.update = AsyncMock(return_value=mock_updated_role)

    response = await roles_controller.update_role(role_id, payload, mock_db_session)

    assert response.description == "A new description"
    mock_role_service.return_value.roles.update.assert_called_once_with(role_id, payload.model_dump(exclude_none=True))

@pytest.mark.anyio
async def test_update_role_not_found(roles_controller: RolesController, mock_db_session: AsyncSession, mock_role_service):
    """Test updating a non-existent role."""
    role_id = uuid4()
    payload = RoleUpdate(description="A new description")
    mock_role_service.return_value.roles.update = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc_info:
        await roles_controller.update_role(role_id, payload, mock_db_session)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Ruolo non trovato" in exc_info.value.detail

# ------------------------------
# delete_role Tests
# ------------------------------

@pytest.mark.anyio
async def test_delete_role_success(roles_controller: RolesController, mock_db_session: AsyncSession, mock_role_service):
    """Test successful deletion of a role."""
    role_id = uuid4()
    mock_role_service.return_value.roles.delete = AsyncMock(return_value=True)

    response = await roles_controller.delete_role(role_id, mock_db_session)

    assert response == {"deleted": True}
    mock_role_service.return_value.roles.delete.assert_called_once_with(role_id)

@pytest.mark.anyio
async def test_delete_role_not_found(roles_controller: RolesController, mock_db_session: AsyncSession, mock_role_service):
    """Test deleting a non-existent role."""
    role_id = uuid4()
    mock_role_service.return_value.roles.delete = AsyncMock(return_value=False)

    with pytest.raises(HTTPException) as exc_info:
        await roles_controller.delete_role(role_id, mock_db_session)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Ruolo non trovato" in exc_info.value.detail
