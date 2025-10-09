# app/Router/news_impacts_router.py
from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.Controllers.news_impact_controller import NewsImpactController
from app.Schemas.news_impact import NewsImpactRead, NewsImpactCreate, NewsImpactUpdate
from app.Router.dependencies import get_current_user

# ------------------------------------------------------------------------------
# Istanze Controller (stateless)
# ------------------------------------------------------------------------------
news_impacts = NewsImpactController()

# ------------------------------------------------------------------------------
# Router
# ------------------------------------------------------------------------------
router = APIRouter()

# ------------------------------------------------------------------------------
# Rotte Utente Autenticato (/me)
# ------------------------------------------------------------------------------
router.get(
    "/me/news-impacts",
    response_model=List[NewsImpactRead],
    tags=["News Impacts"],
    summary="Lista i miei news impacts",
    dependencies=[Depends(get_current_user)],
)(news_impacts.list_my_news_impacts)

router.post(
    "/me/news-impacts",
    response_model=NewsImpactRead,
    status_code=status.HTTP_201_CREATED,
    tags=["News Impacts"],
    summary="Crea un nuovo news impact",
    dependencies=[Depends(get_current_user)],
)(news_impacts.create_news_impact)

# ------------------------------------------------------------------------------
# Rotte per ID specifico (con controllo di ownership)
# ------------------------------------------------------------------------------
router.get(
    "/news-impacts/{news_impact_id}",
    response_model=NewsImpactRead,
    tags=["News Impacts"],
    summary="Recupera un news impact per ID",
)(news_impacts.get_news_impact)

router.put(
    "/news-impacts/{news_impact_id}",
    response_model=NewsImpactRead,
    tags=["News Impacts"],
    summary="Aggiorna un news impact per ID",
)(news_impacts.update_news_impact)

router.delete(
    "/news-impacts/{news_impact_id}",
    status_code=status.HTTP_200_OK,
    tags=["News Impacts"],
    summary="Elimina un news impact per ID",
)(news_impacts.delete_news_impact)