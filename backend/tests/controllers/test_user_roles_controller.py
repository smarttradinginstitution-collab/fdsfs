import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.Controllers.user_roles_controller import UserRolesController
from app.Schemas.user_role import AssignRoleInput
from app.Models.role import Role

# ------------------------------
# Fixtures
# ------------------------------

@pytest.fixture
def user_roles_controller():
    """Returns an instance of the UserRolesController."""
    return UserRolesController()

@pytest.fixture
def mock_db_session():
    """Provides a mock AsyncSession."""
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def mock_role_service(mocker):
    """Mocks the RoleService."""
    return mocker.patch("app.Controllers.user_roles_controller.RoleService")

# ------------------------------
# list_user_roles Tests
# ------------------------------

@pytest.mark.anyio
async def test_list_user_roles_success(user_roles_controller: UserRolesController, mock_db_session: AsyncSession, mock_role_service):
    """Test successful retrieval of roles for a user."""
    user_id = uuid4()
    mock_roles = [Role(id=uuid4(), name="admin"), Role(id=uuid4(), name="user")]
    mock_role_service.return_value.user_roles.list_user_roles = AsyncMock(return_value=mock_roles)

    response = await user_roles_controller.list_user_roles(user_id, mock_db_session)

    assert len(response) == 2
    assert response[0].name == "admin"
    mock_role_service.return_value.user_roles.list_user_roles.assert_called_once_with(user_id)

# ------------------------------
# assign_role Tests
# ------------------------------

@pytest.mark.anyio
async def test_assign_role_success(user_roles_controller: UserRolesController, mock_db_session: AsyncSession, mock_role_service):
    """Test successful assignment of a role to a user."""
    user_id = uuid4()
    role_id = uuid4()
    payload = AssignRoleInput(user_id=user_id, role_id=role_id)
    mock_role = Role(id=role_id, name="new_role")

    mock_role_service.return_value.user_roles.assign = AsyncMock()
    mock_role_service.return_value.roles.get = AsyncMock(return_value=mock_role)

    response = await user_roles_controller.assign_role(payload, mock_db_session)

    assert response.id == role_id
    assert response.name == "new_role"
    mock_role_service.return_value.user_roles.assign.assert_called_once_with(user_id, role_id)
    mock_role_service.return_value.roles.get.assert_called_once_with(role_id)

@pytest.mark.anyio
async def test_assign_role_but_role_not_found_after(user_roles_controller: UserRolesController, mock_db_session: AsyncSession, mock_role_service):
    """Test edge case where role is not found after assignment."""
    user_id = uuid4()
    role_id = uuid4()
    payload = AssignRoleInput(user_id=user_id, role_id=role_id)

    mock_role_service.return_value.user_roles.assign = AsyncMock()
    mock_role_service.return_value.roles.get = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc_info:
        await user_roles_controller.assign_role(payload, mock_db_session)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Ruolo non trovato dopo l'assegnazione" in exc_info.value.detail

# ------------------------------
# unassign_role Tests
# ------------------------------

@pytest.mark.anyio
async def test_unassign_role_success(user_roles_controller: UserRolesController, mock_db_session: AsyncSession, mock_role_service):
    """Test successful unassignment of a role from a user."""
    user_id = uuid4()
    role_id = uuid4()
    mock_role_service.return_value.user_roles.unassign = AsyncMock(return_value=True)

    response = await user_roles_controller.unassign_role(user_id, role_id, mock_db_session)

    assert response == {"deleted": True}
    mock_role_service.return_value.user_roles.unassign.assert_called_once_with(user_id, role_id)

@pytest.mark.anyio
async def test_unassign_role_not_found(user_roles_controller: UserRolesController, mock_db_session: AsyncSession, mock_role_service):
    """Test unassigning a role that is not assigned."""
    user_id = uuid4()
    role_id = uuid4()
    mock_role_service.return_value.user_roles.unassign = AsyncMock(return_value=False)

    with pytest.raises(HTTPException) as exc_info:
        await user_roles_controller.unassign_role(user_id, role_id, mock_db_session)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Assegnazione non trovata" in exc_info.value.detail
