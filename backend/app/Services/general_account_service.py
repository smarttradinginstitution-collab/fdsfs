# app/Services/general_account_service.py
from __future__ import annotations

from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status

import copy
from app.Repositories.general_account_repository import GeneralAccountRepository
from app.Schemas.general_account import (
    GeneralAccountCreate,
    GeneralAccountRead,
    GeneralAccountWithData,
)
from app.Schemas.tag import TagCreate
from app.Schemas.tags_group import TagsGroupCreate
from app.Infrastructure.db import get_db
from app.Services.notebook_service import NotebookService
from app.Services.tags_group_service import TagsGroupService
from app.Services.tag_service import TagService

DEFAULT_TAGS_STRUCTURE = [
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


class GeneralAccountService:
    def __init__(
        self,
        db: AsyncSession = Depends(get_db),
    ):
        self.db = db
        self.repo = GeneralAccountRepository(db)

    async def _create_default_tags_and_groups(
        self,
        general_account_id: UUID,
        tags_group_service: TagsGroupService,
        tag_service: TagService,
    ):
        """Creates the default tags and groups for a new general account."""
        structure_copy = copy.deepcopy(DEFAULT_TAGS_STRUCTURE)
        for group_data in structure_copy:
            tags_to_create = group_data.pop("tags")
            group_schema = TagsGroupCreate(**group_data)
            created_group = await tags_group_service.create_tags_group(
                tags_group_data=group_schema, general_account_id=general_account_id
            )

            for tag_data in tags_to_create:
                tag_schema = TagCreate(
                    name=tag_data["name"],
                    color=tag_data["color"],
                    group_id=created_group.id,
                )
                await tag_service.create_tag(tag_schema)

    async def create_general_account_for_user(
        self,
        claims: dict,
        notebook_service: NotebookService,
        tags_group_service: TagsGroupService,
        tag_service: TagService,
    ) -> GeneralAccountRead:
        """
        Crea un GeneralAccount per l'utente corrente, usando la sua email come label.
        """
        user_id = UUID(claims["sub"])
        user_email = claims["email"]

        account_create_schema = GeneralAccountCreate(label=user_email)

        db_account = await self.repo.create_general_account(
            user_id=user_id, account_data=account_create_schema
        )

        # Automatically create system folders for the new account
        await notebook_service._ensure_system_folders_exist(db_account.id)

        # Create default tags and groups
        await self._create_default_tags_and_groups(
            general_account_id=db_account.id,
            tags_group_service=tags_group_service,
            tag_service=tag_service,
        )

        return GeneralAccountRead.model_validate(db_account)

    async def get_general_account_for_user(
        self, claims: dict
    ) -> Optional[GeneralAccountRead]:
        """Recupera il GeneralAccount per l'utente corrente."""
        user_id = UUID(claims["sub"])
        db_account = await self.repo.get_by_user_id(user_id=user_id)
        if db_account:
            return GeneralAccountRead.model_validate(db_account)
        return None

    async def get_general_account_with_all_data(
        self, account_id: UUID, claims: dict
    ) -> GeneralAccountWithData:
        """
        Recupera un GeneralAccount con tutte le sue relazioni (mistakes, news, ecc.)
        verificando che l'utente sia il proprietario.
        """
        user_id = UUID(claims["sub"])
        db_account = await self.repo.get_by_id_with_all_data(account_id=account_id)

        if not db_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="General account not found.",
            )

        if db_account.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not authorized to access this account.",
            )

        return GeneralAccountWithData.model_validate(db_account)