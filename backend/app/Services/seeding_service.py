# backend/app/Services/seeding_service.py
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.Models.tags_group import TagsGroup
from app.Models.tag import Tag

async def seed_default_tags_for_account(general_account_id: UUID, db: AsyncSession):
    """
    Seeds the default tag groups and tags for a new general account.
    This function is designed to be idempotent.
    """
    # Define the default structure
    default_structure = {
        "Setup": {
            "description": "The chart pattern or technical setup that initiated the trade.",
            "tags": ["Breakout", "Reversal", "Continuation", "Fakeout"],
        },
        "Market Context": {
            "description": "The overall market conditions at the time of the trade.",
            "tags": ["Trending Market", "Ranging Market", "High Volatility", "Low Volume"],
        },
        "Execution": {
            "description": "How you actively managed the entry, position, and exit.",
            "tags": ["Scaled In", "Took Partials", "Moved to Breakeven", "All In / All Out"],
        },
        "Timeframe": {
            "description": "The primary timeframe used for the trade analysis.",
            "tags": ["1m", "5m", "15m", "1h", "Daily"],
        },
    }

    for group_name, group_data in default_structure.items():
        # Check if group already exists
        existing_group = await db.execute(
            select(TagsGroup).where(
                TagsGroup.general_account_id == general_account_id,
                TagsGroup.name == group_name
            )
        )
        if existing_group.scalars().first():
            continue

        # Create the group
        new_group = TagsGroup(
            general_account_id=general_account_id,
            name=group_name,
            description=group_data["description"],
        )
        db.add(new_group)
        await db.flush()  # Flush to get the new_group.id

        # Create the tags for the new group
        for tag_name in group_data["tags"]:
            new_tag = Tag(
                name=tag_name,
                group_id=new_group.id
            )
            db.add(new_tag)