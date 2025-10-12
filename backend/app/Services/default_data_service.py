# app/Services/default_data_service.py
from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.Repositories.tags_group_repository import TagsGroupRepository
from app.Repositories.tag_repository import TagRepository
from app.Schemas.tags_group import TagsGroupCreate
from app.Schemas.tag import TagCreate


class DefaultDataService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.tags_group_repo = TagsGroupRepository(db)
        self.tag_repo = TagRepository(db)

    async def create_default_tags_for_account(self, general_account_id: UUID):
        """
        Crea i gruppi di tag e i tag predefiniti per un nuovo account generale.
        Questa funzione non committa la transazione, permettendo al chiamante di gestirla.
        """
        default_data = self._get_default_data()

        for group_data in default_data["tags_groups"]:
            tags = group_data.pop("tags")

            tags_group_schema = TagsGroupCreate(**group_data)

            db_tags_group = await self.tags_group_repo.create_tags_group(
                tags_group_data=tags_group_schema,
                general_account_id=general_account_id,
            )

            # Eseguiamo un flush per ottenere l'ID del gruppo appena creato
            await self.db.flush()

            for tag_data in tags:
                tag_schema = TagCreate(group_id=db_tags_group.id, **tag_data)
                await self.tag_repo.create_tag(tag_data=tag_schema)

    def _get_default_data(self):
        """
        Restituisce la struttura dei dati predefiniti per tag e gruppi di tag.
        """
        return {
            "tags_groups": [
                {
                    "name": "Setup",
                    "description": "The chart pattern or technical setup that initiated the trade.",
                    "color": "#888888",
                    "position": 1,
                    "tags": [
                        {"name": "Breakout", "color": "#888888"},
                        {"name": "Reversal", "color": "#888888"},
                        {"name": "Continuation", "color": "#888888"},
                        {"name": "Fakeout", "color": "#888888"},
                    ],
                },
                {
                    "name": "Market Context",
                    "description": "The overall market conditions at the time of the trade.",
                    "color": "#888888",
                    "position": 2,
                    "tags": [
                        {"name": "Trending Market", "color": "#888888"},
                        {"name": "Ranging Market", "color": "#888888"},
                        {"name": "High Volatility", "color": "#888888"},
                        {"name": "Low Volume", "color": "#888888"},
                    ],
                },
                {
                    "name": "Execution",
                    "description": "How you actively managed the entry, position, and exit.",
                    "color": "#888888",
                    "position": 3,
                    "tags": [
                        {"name": "Scaled In", "color": "#888888"},
                        {"name": "Took Partials", "color": "#888888"},
                        {"name": "Moved to Breakeven", "color": "#888888"},
                        {"name": "All In / All Out", "color": "#888888"},
                    ],
                },
                {
                    "name": "Timeframe",
                    "description": "The primary timeframe used for the trade analysis.",
                    "color": "#888888",
                    "position": 4,
                    "tags": [
                        {"name": "1m", "color": "#888888"},
                        {"name": "5m", "color": "#888888"},
                        {"name": "15m", "color": "#888888"},
                        {"name": "1h", "color": "#888888"},
                        {"name": "Daily", "color": "#888888"},
                    ],
                },
            ]
        }