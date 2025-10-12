# app/Services/general_account_service.py
from __future__ import annotations
import json
from uuid import UUID
from typing import Optional, Tuple, Any

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status

from app.Repositories.general_account_repository import GeneralAccountRepository
from app.Schemas.general_account import (
    GeneralAccountCreate,
    GeneralAccountRead,
    GeneralAccountWithData,
)
from app.Infrastructure.db import get_db
from app.Services.notebook_service import NotebookService
from app.Services.tags_group_service import TagsGroupService
from app.Services.tag_service import TagService
from app.Schemas.tags_group import TagsGroupCreate
from app.Schemas.tag import TagCreate


class GeneralAccountService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
        self.repo = GeneralAccountRepository(db)

    async def create_general_account_for_user(
        self,
        claims: dict,
        notebook_service: NotebookService,
        tags_group_service: TagsGroupService,
        tag_service: TagService,
    ) -> Tuple[GeneralAccountRead, bool]:
        """
        Crea un GeneralAccount per l'utente corrente, usando la sua email come label.
        Se l'account esiste già, lo restituisce. Altrimenti, lo crea e popola
        i dati iniziali (tags, etc.).
        Restituisce l'account e un booleano che indica se è stato creato.
        """
        user_id = UUID(claims["sub"])

        # 1. Controlla se l'account esiste già
        existing_account = await self.repo.get_by_user_id(user_id=user_id)
        if existing_account:
            return GeneralAccountRead.model_validate(existing_account), False

        # 2. Se non esiste, crea il nuovo account
        user_email = claims["email"]
        account_create_schema = GeneralAccountCreate(label=user_email)

        try:
            db_account = await self.repo.create_general_account(
                user_id=user_id, account_data=account_create_schema
            )

            # Crea le cartelle di sistema e i dati di default
            await notebook_service._ensure_system_folders_exist(db_account.id)
            await self._create_default_tags_and_groups(
                general_account_id=db_account.id,
                tags_group_service=tags_group_service,
                tag_service=tag_service,
            )

            # Commit della transazione completa
            await self.db.commit()

            # Ricarica l'account con tutte le relazioni per la risposta
            refreshed_account = await self.repo.get_by_id_with_all_data(db_account.id)
            return GeneralAccountRead.model_validate(refreshed_account), True

        except IntegrityError:
            await self.db.rollback()
            # Race condition: un altro processo ha creato l'account nel frattempo.
            # Recuperalo e restituiscilo.
            existing_account = await self.repo.get_by_user_id(user_id=user_id)
            if not existing_account:
                # Questo non dovrebbe accadere, ma per sicurezza...
                raise HTTPException(status_code=500, detail="Failed to create or find general account after race condition.")
            return GeneralAccountRead.model_validate(existing_account), False

    async def _create_default_tags_and_groups(
        self,
        general_account_id: UUID,
        tags_group_service: TagsGroupService,
        tag_service: TagService,
    ):
        """Crea i gruppi di tag e i tag predefiniti per un nuovo account."""
        default_data = {
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

        for group_data in default_data["tags_groups"]:
            tags = group_data.pop("tags")

            # Crea il gruppo di tag
            group_schema = TagsGroupCreate(**group_data)
            created_group = await tags_group_service.repo.create_tags_group(
                tags_group_data=group_schema, general_account_id=general_account_id
            )
            await self.db.flush() # Assicura che l'ID del gruppo sia disponibile

            # Crea i tag per questo gruppo
            for tag_data in tags:
                tag_schema = TagCreate(
                    name=tag_data["name"],
                    color=tag_data["color"],
                    group_id=created_group.id,
                )
                await tag_service.tag_repo.create_tag(tag_schema)

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