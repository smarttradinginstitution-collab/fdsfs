# app/Controllers/general_account_controller.py
from __future__ import annotations
from uuid import UUID
from fastapi import Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

# Importa i servizi e i controller necessari
from app.Services.general_account_service import GeneralAccountService
from app.Services.notebook_service import NotebookService
from app.Controllers.tags_group_controller import create_tags_group
from app.Controllers.tag_controller import TagController

# Importa schemi e dipendenze
from app.Schemas.tags_group import TagsGroupCreate
from app.Schemas.tag import TagCreate
from app.Router.auth import get_current_claims
from app.Infrastructure.db import get_db

async def create_general_account(
    response: Response,
    claims: dict = Depends(get_current_claims),
    service: GeneralAccountService = Depends(),
    notebook_service: NotebookService = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Crea un General Account per l'utente autenticato. Se l'account esiste già,
    lo restituisce. Altrimenti, lo crea e popola i dati iniziali (tags, etc.).
    """
    account, created = await service.create_general_account_for_user(
        claims=claims, notebook_service=notebook_service
    )

    if created:
        response.status_code = status.HTTP_201_CREATED
    else:
        response.status_code = status.HTTP_200_OK
        # Se l'account esisteva già, non è necessario continuare
        return account

    # E popola i dati di default
    default_data = {
        "tags_groups": [
            { "name": "Setup", "description": "The chart pattern or technical setup that initiated the trade.", "color": "#888888", "position": 1, "tags": [ { "name": "Breakout", "color": "#888888" }, { "name": "Reversal", "color": "#888888" }, { "name": "Continuation", "color": "#888888" }, { "name": "Fakeout", "color": "#888888" } ] },
            { "name": "Market Context", "description": "The overall market conditions at the time of the trade.", "color": "#888888", "position": 2, "tags": [ { "name": "Trending Market", "color": "#888888" }, { "name": "Ranging Market", "color": "#888888" }, { "name": "High Volatility", "color": "#888888" }, { "name": "Low Volume", "color": "#888888" } ] },
            { "name": "Execution", "description": "How you actively managed the entry, position, and exit.", "color": "#888888", "position": 3, "tags": [ { "name": "Scaled In", "color": "#888888" }, { "name": "Took Partials", "color": "#888888" }, { "name": "Moved to Breakeven", "color": "#888888" }, { "name": "All In / All Out", "color": "#888888" } ] },
            { "name": "Timeframe", "description": "The primary timeframe used for the trade analysis.", "color": "#888888", "position": 4, "tags": [ { "name": "1m", "color": "#888888" }, { "name": "5m", "color": "#888888" }, { "name": "15m", "color": "#888888" }, { "name": "1h", "color": "#888888" }, { "name": "Daily", "color": "#888888" } ] }
        ]
    }

    tag_controller = TagController()

    for group_data in default_data["tags_groups"]:
        tags_to_create = group_data.pop("tags")

        group_schema = TagsGroupCreate(**group_data)
        created_group = await create_tags_group(
            tags_group_data=group_schema,
            general_account_id=account.id,
            db=db
        )

        for tag_data in tags_to_create:
            tag_schema = TagCreate(
                name=tag_data["name"],
                color=tag_data["color"],
                group_id=created_group.id
            )
            await tag_controller.create_tag(
                tag_data=tag_schema,
                general_account_id=account.id,
                db=db
            )

    # Ricarica l'account per includere i nuovi dati
    refreshed_account = await service.get_general_account_with_all_data(
        claims=claims, account_id=account.id
    )
    return refreshed_account


async def get_my_general_account(
    claims: dict = Depends(get_current_claims),
    service: GeneralAccountService = Depends(),
):
    """
    Recupera il General Account associato all'utente autenticato.
    """
    # Delega il recupero dell'account al servizio.
    account = await service.get_general_account_for_user(claims)
    # Se il servizio non trova un account, solleva un'eccezione HTTP 404.
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="General Account non trovato per questo utente.",
        )
    return account


async def get_general_account_with_all_data(
    account_id: UUID,
    claims: dict = Depends(get_current_claims),
    service: GeneralAccountService = Depends(),
):
    """
    Recupera un General Account con tutte le sue relazioni (mistakes, news, ecc.).
    """
    account = await service.get_general_account_with_all_data(
        account_id=account_id, claims=claims
    )
    return account