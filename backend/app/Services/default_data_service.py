# app/Services/default_data_service.py
from __future__ import annotations
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.Repositories.tags_group_repository import TagsGroupRepository
from app.Repositories.tag_repository import TagRepository
from app.Schemas.tags_group import TagsGroupCreate
from app.Schemas.tag import TagCreate
from app.Infrastructure.db import get_db

# Struttura dei dati di default
DEFAULT_TAGS_STRUCTURE = [
    {
        "group_name": "Setup",
        "description": "The chart pattern or technical setup that initiated the trade.",
        "tags": ["Breakout", "Reversal", "Continuation", "Fakeout"],
    },
    {
        "group_name": "Market Context",
        "description": "The overall market conditions at the time of the trade.",
        "tags": ["Trending Market", "Ranging Market", "High Volatility", "Low Volume"],
    },
    {
        "group_name": "Execution",
        "description": "How you actively managed the entry, position, and exit.",
        "tags": ["Scaled In", "Took Partials", "Moved to Breakeven", "All In / All Out"],
    },
    {
        "group_name": "Timeframe",
        "description": "The primary timeframe used for the trade analysis.",
        "tags": ["1m", "5m", "15m", "1h", "Daily"],
    },
]

class DefaultDataService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
        self.tags_group_repo = TagsGroupRepository(db)
        self.tag_repo = TagRepository(db)

    async def create_default_tags_for_account(self, general_account_id: UUID):
        """
        Creates the default tag groups and tags for a new general account,
        ensuring not to create duplicates.
        """
        # Get existing group names to avoid creating duplicates
        existing_groups = await self.tags_group_repo.list_tags_groups_by_general_account_id(general_account_id)
        existing_group_names = {group.name for group in existing_groups}

        for group_data in DEFAULT_TAGS_STRUCTURE:
            if group_data["group_name"] in existing_group_names:
                continue  # Skip if group already exists

            # Create the tag group
            group_schema = TagsGroupCreate(
                name=group_data["group_name"],
                description=group_data["description"],
                color="#888888",
                position=0,
            )
            db_group = await self.tags_group_repo.create_tags_group(
                tags_group_data=group_schema, general_account_id=general_account_id
            )

            # Re-fetch the group to ensure it's session-attached for the loop
            refreshed_group = await self.tags_group_repo.get_tags_group_by_id(
                db_group.id, general_account_id
            )
            if not refreshed_group:
                # This should not happen, but as a safeguard
                continue

            # Create the associated tags
            for tag_name in group_data["tags"]:
                tag_schema = TagCreate(
                    name=tag_name, group_id=refreshed_group.id, color="#888888"
                )
                await self.tag_repo.create_tag(tag_data=tag_schema)