from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.Controllers.news_impact_controller import NewsImpactController
from app.Schemas.news_impact import NewsImpactRead, NewsImpactCreate, NewsImpactUpdate
from app.Router.dependencies import get_current_user

# ------------------------------------------------------------------------------
# Controller Instances (stateless)
# ------------------------------------------------------------------------------
news_impacts = NewsImpactController()

# ------------------------------------------------------------------------------
# Router
# ------------------------------------------------------------------------------
router = APIRouter()

# ------------------------------------------------------------------------------
# Authenticated User Routes (/me)
# ------------------------------------------------------------------------------
router.get(
    "/me/news-impacts",
    response_model=List[NewsImpactRead],
    tags=["News Impacts"],
    summary="List my news impacts",
    dependencies=[Depends(get_current_user)],
)(news_impacts.list_my_news_impacts)

router.post(
    "/me/news-impacts",
    response_model=NewsImpactRead,
    status_code=status.HTTP_201_CREATED,
    tags=["News Impacts"],
    summary="Create a new news impact",
    dependencies=[Depends(get_current_user)],
)(news_impacts.create_news_impact)

# ------------------------------------------------------------------------------
# Routes by specific ID (with ownership check)
# ------------------------------------------------------------------------------
router.get(
    "/news-impacts/{news_impact_id}",
    response_model=NewsImpactRead,
    tags=["News Impacts"],
    summary="Get a news impact by ID",
)(news_impacts.get_news_impact)

router.put(
    "/news-impacts/{news_impact_id}",
    response_model=NewsImpactRead,
    tags=["News Impacts"],
    summary="Update a news impact by ID",
)(news_impacts.update_news_impact)

router.delete(
    "/news-impacts/{news_impact_id}",
    status_code=status.HTTP_200_OK,
    tags=["News Impacts"],
    summary="Delete a news impact by ID",
)(news_impacts.delete_news_impact)