# app/Router/platform_router.py
from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.Controllers.platform_controller import PlatformController
from app.Infrastructure.db import get_db
from app.Schemas.platform import Platform, PlatformCreate, PlatformSummary, PlatformUpdate

router = APIRouter(prefix="/platforms", tags=["Platforms"])


@router.post("/", response_model=Platform, status_code=201)
async def create_platform(
    platform_in: PlatformCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new platform.
    """
    return await PlatformController(db).create_platform(platform_in)


@router.get("/", response_model=List[Platform])
async def read_platforms(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    """
    Retrieve all platforms with pagination.
    """
    return await PlatformController(db).get_all_platforms(skip=skip, limit=limit)


@router.get("/{platform_id}", response_model=Platform)
async def read_platform(
    platform_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve a single platform by its ID.
    """
    return await PlatformController(db).get_platform_by_id(platform_id)


@router.get("/{platform_id}/summary", response_model=PlatformSummary)
async def read_platform_summary(
    platform_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve a single platform with its associated brokers.
    """
    return await PlatformController(db).get_platform_summary(platform_id)


@router.put("/{platform_id}", response_model=Platform)
async def update_platform(
    platform_id: uuid.UUID,
    platform_in: PlatformUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update an existing platform.
    """
    return await PlatformController(db).update_platform(platform_id, platform_in)


@router.delete("/{platform_id}", response_model=Platform)
async def delete_platform(
    platform_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a platform by its ID.
    """
    return await PlatformController(db).delete_platform(platform_id)