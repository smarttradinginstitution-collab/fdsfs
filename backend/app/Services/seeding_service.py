# app/Services/seeding_service.py
import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.Models.tags_group import TagsGroup
from app.Models.tag import Tag

logger = logging.getLogger(__name__)

DEFAULT_TAGS = {
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

async def seed_default_tags_for_account(general_account_id: UUID, db: AsyncSession):
    """
    Seeds the database with a default set of tag groups and tags for a new general account.
    """
    logger.info(f"Seeding default tags for general_account_id: {general_account_id}")
    try:
        for group_name, group_data in DEFAULT_TAGS.items():
            # Create the TagsGroup
            new_group = TagsGroup(
                name=group_name,
                description=group_data["description"],
                general_account_id=general_account_id,
            )
            db.add(new_group)
            await db.flush()  # Flush to get the new_group.id
            logger.info(f"Created tag group: {group_name} with id: {new_group.id}")

            # Create the associated Tags
            for tag_name in group_data["tags"]:
                new_tag = Tag(
                    name=tag_name,
                    group_id=new_group.id,
                )
                db.add(new_tag)
                await db.flush() # Flush to get the new_tag.id
                logger.info(f"Created tag: {tag_name} for group: {group_name} with id: {new_tag.id}")
        logger.info("Successfully seeded default tags.")
    except Exception as e:
        logger.error(f"Error seeding default tags: {e}")
        await db.rollback()
        raise