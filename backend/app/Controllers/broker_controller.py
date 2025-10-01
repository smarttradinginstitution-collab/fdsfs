# app/Controllers/broker_controller.py
from __future__ import annotations

import uuid
from typing import List
from fastapi import APIRouter, Depends, status

from app.Services.broker_service import BrokerService
from app.Schemas.broker import BrokerRead, BrokerCreate, BrokerUpdate
from app.Schemas.asset_class import AssetClassRead
from app.Schemas.broker_asset_class import BrokerAssetClassCreate, BrokerAssetClassRead
from app.Router.auth import require_roles

router = APIRouter(
    prefix="/brokers",
    tags=["Brokers"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/",
    response_model=BrokerRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new broker (admin only)",
    dependencies=[Depends(require_roles(["admin"]))],
)
async def create_broker(
    broker_data: BrokerCreate,
    service: BrokerService = Depends(),
):
    """
    Creates a new broker.
    - **name**: The name of the broker (must be unique).
    """
    return await service.create_broker(broker_data)


@router.get("/", response_model=List[BrokerRead], summary="Get all brokers")
async def get_all_brokers(
    service: BrokerService = Depends(),
):
    """
    Retrieves a list of all available brokers.
    """
    return await service.get_all_brokers()


@router.get("/{broker_id}", response_model=BrokerRead, summary="Get a broker by ID")
async def get_broker_by_id(
    broker_id: uuid.UUID,
    service: BrokerService = Depends(),
):
    """
    Retrieves a single broker by its unique ID.
    """
    return await service.get_broker_by_id(broker_id)


@router.put(
    "/{broker_id}",
    response_model=BrokerRead,
    summary="Update a broker (admin only)",
    dependencies=[Depends(require_roles(["admin"]))],
)
async def update_broker(
    broker_id: uuid.UUID,
    broker_data: BrokerUpdate,
    service: BrokerService = Depends(),
):
    """
    Updates a broker's name.
    - **name**: The new name for the broker (must be unique).
    """
    return await service.update_broker(broker_id, broker_data)


@router.delete(
    "/{broker_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a broker (admin only)",
    dependencies=[Depends(require_roles(["admin"]))],
)
async def delete_broker(
    broker_id: uuid.UUID,
    service: BrokerService = Depends(),
):
    """
    Deletes a broker by its unique ID.
    Deletion will fail if the broker is associated with any other resources.
    """
    await service.delete_broker(broker_id)
    return None


@router.get(
    "/{broker_id}/asset-classes",
    response_model=List[AssetClassRead],
    summary="Get associated asset classes for a broker (admin only)",
    dependencies=[Depends(require_roles(["admin"]))],
)
async def get_associated_asset_classes(
    broker_id: uuid.UUID,
    service: BrokerService = Depends(),
):
    """
    Retrieves a list of asset classes associated with a specific broker.
    """
    return await service.get_associated_asset_classes(broker_id)


@router.post(
    "/{broker_id}/asset-classes",
    response_model=BrokerAssetClassRead,
    status_code=status.HTTP_201_CREATED,
    summary="Associate an asset class with a broker (admin only)",
    dependencies=[Depends(require_roles(["admin"]))],
)
async def add_asset_class_to_broker(
    broker_id: uuid.UUID,
    association_data: BrokerAssetClassCreate,
    service: BrokerService = Depends(),
):
    """
    Associates an asset class with a broker.
    - **asset_class_id**: The ID of the asset class to associate.
    """
    return await service.add_asset_class_to_broker(broker_id, association_data)


@router.delete(
    "/{broker_id}/asset-classes/{asset_class_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Disassociate an asset class from a broker (admin only)",
    dependencies=[Depends(require_roles(["admin"]))],
)
async def remove_asset_class_from_broker(
    broker_id: uuid.UUID,
    asset_class_id: uuid.UUID,
    service: BrokerService = Depends(),
):
    """
    Disassociates an asset class from a broker by their unique IDs.
    """
    await service.remove_asset_class_from_broker(broker_id, asset_class_id)
    return None
