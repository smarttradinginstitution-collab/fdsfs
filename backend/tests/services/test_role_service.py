# backend/tests/services/test_role_service.py

import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.Services.role_service import RoleService
from app.Models.role import Role
from app.Models.user_role import UserRole


@pytest.fixture
def role_service(db_session: AsyncSession):
    return RoleService(db=db_session)


@pytest.mark.asyncio
async def test_list_roles_for_user(role_service: RoleService):
    # Arrange
    user_id = uuid4()
    role_service.user_roles = AsyncMock()
    expected_roles = [Role(id=uuid4(), name="admin"), Role(id=uuid4(), name="user")]
    role_service.user_roles.list_user_roles.return_value = expected_roles

    # Act
    result = await role_service.list_roles_for_user(user_id)

    # Assert
    assert result == expected_roles
    role_service.user_roles.list_user_roles.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_assign_role_to_user(role_service: RoleService):
    # Arrange
    user_id = uuid4()
    role_id = uuid4()
    role_service.user_roles = AsyncMock()
    expected_user_role = UserRole(user_id=user_id, role_id=role_id)
    role_service.user_roles.assign.return_value = expected_user_role

    # Act
    result = await role_service.assign_role_to_user(user_id, role_id)

    # Assert
    assert result == expected_user_role
    role_service.user_roles.assign.assert_called_once_with(user_id, role_id)


@pytest.mark.asyncio
async def test_unassign_role_from_user(role_service: RoleService):
    # Arrange
    user_id = uuid4()
    role_id = uuid4()
    role_service.user_roles = AsyncMock()
    role_service.user_roles.unassign.return_value = True

    # Act
    result = await role_service.unassign_role_from_user(user_id, role_id)

    # Assert
    assert result is True
    role_service.user_roles.unassign.assert_called_once_with(user_id, role_id)
