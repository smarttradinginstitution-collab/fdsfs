import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.tag import Tag
from app.Repositories.tag_repository import TagRepository

@pytest.mark.anyio
async def test_upsert_by_name_creates_new_tag_if_not_exists():
    """
    Test that upsert_by_name creates a new tag if it doesn't exist.
    """
    mock_session = AsyncMock(spec=AsyncSession)

    # Mock for the SELECT query
    mock_select_result = MagicMock()
    mock_select_result.scalars.return_value.first.return_value = None

    # Mock for the INSERT query
    new_tag = Tag(id=uuid4(), user_id=uuid4(), name="New Tag", color="#FF0000")
    mock_insert_result = MagicMock()
    mock_insert_result.scalar_one.return_value = new_tag

    # When execute is called, return the appropriate mock result
    mock_session.execute.side_effect = [
        mock_select_result,
        mock_insert_result,
    ]

    repo = TagRepository(mock_session)
    result = await repo.upsert_by_name(user_id=new_tag.user_id, name=new_tag.name, color=new_tag.color)

    assert result == new_tag
    assert mock_session.execute.call_count == 2
    assert mock_session.flush.call_count == 1

@pytest.mark.anyio
async def test_upsert_by_name_updates_color_if_different():
    """
    Test that upsert_by_name updates the color of an existing tag if the color is different.
    """
    mock_session = AsyncMock(spec=AsyncSession)

    user_id = uuid4()
    tag_name = "Existing Tag"
    old_color = "#0000FF"
    new_color = "#FF0000"

    existing_tag = Tag(id=uuid4(), user_id=user_id, name=tag_name, color=old_color)

    mock_select_result = MagicMock()
    mock_select_result.scalars.return_value.first.return_value = existing_tag
    mock_session.execute.return_value = mock_select_result

    repo = TagRepository(mock_session)
    result = await repo.upsert_by_name(user_id=user_id, name=tag_name, color=new_color)

    assert result.color == new_color
    assert mock_session.flush.call_count == 1

@pytest.mark.anyio
async def test_upsert_by_name_does_not_update_if_color_is_same():
    """
    Test that upsert_by_name does not update an existing tag if the color is the same.
    """
    mock_session = AsyncMock(spec=AsyncSession)

    user_id = uuid4()
    tag_name = "Existing Tag"
    same_color = "#0000FF"

    existing_tag = Tag(id=uuid4(), user_id=user_id, name=tag_name, color=same_color)

    mock_select_result = MagicMock()
    mock_select_result.scalars.return_value.first.return_value = existing_tag
    mock_session.execute.return_value = mock_select_result

    repo = TagRepository(mock_session)
    result = await repo.upsert_by_name(user_id=user_id, name=tag_name, color=same_color)

    assert result.color == same_color
    assert mock_session.flush.call_count == 0

@pytest.mark.anyio
async def test_list_user_tags():
    """
    Test that list_user_tags returns a sequence of tags for a given user.
    """
    mock_session = AsyncMock(spec=AsyncSession)
    user_id = uuid4()

    tags = [
        Tag(id=uuid4(), user_id=user_id, name="Tag 1", color="#FF0000"),
        Tag(id=uuid4(), user_id=user_id, name="Tag 2", color="#00FF00"),
    ]

    mock_select_result = MagicMock()
    mock_select_result.scalars.return_value.all.return_value = tags
    mock_session.execute.return_value = mock_select_result

    repo = TagRepository(mock_session)
    result = await repo.list_user_tags(user_id=user_id)

    assert len(result) == 2
    assert result[0].name == "Tag 1"
    assert result[1].name == "Tag 2"
