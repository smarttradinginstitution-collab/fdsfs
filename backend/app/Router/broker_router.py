# app/Router/broker_router.py
# Questo file definisce tutti gli endpoint relativi alla gestione dei broker.
# Separa la definizione della rotta (URL, metodo, tag) dalla logica di business.
from __future__ import annotations

import uuid
from typing import List
from fastapi import APIRouter, Depends, status

# Importa le funzioni del controller che contengono la logica effettiva.
from app.Controllers import broker_controller

# Importa gli schemi Pydantic per la validazione e la serializzazione.
from app.Schemas.broker import BrokerRead, BrokerCreate, BrokerUpdate
from app.Schemas.asset_class import AssetClassRead
from app.Schemas.broker_asset_class import BrokerAssetClassCreate, BrokerAssetClassRead
# Importa la dipendenza per la gestione dei ruoli.
from app.Router.auth import require_roles

# Definizione del router specifico per i broker.
# Tutte le rotte qui definite avranno il prefisso /brokers e saranno raggruppate
# sotto il tag "Brokers" nella documentazione OpenAPI.
router = APIRouter(
    prefix="/brokers",
    tags=["Brokers"],
    responses={404: {"description": "Not found"}},
)

# ==============================================================================
# ASSOCIAZIONE DELLE ROTTE AI CONTROLLER
# ==============================================================================
# La sintassi `router.post(...)(broker_controller.create_broker)` collega
# un endpoint HTTP a una specifica funzione del controller.

# Rotta per creare un nuovo broker (accessibile solo agli admin).
router.post(
    "/",
    response_model=BrokerRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new broker (admin only)",
    dependencies=[Depends(require_roles(["admin"]))],
)(broker_controller.create_broker)

# Rotta per ottenere la lista di tutti i broker.
router.get("/", response_model=List[BrokerRead], summary="Get all brokers")(
    broker_controller.get_all_brokers
)

# Rotta per ottenere un singolo broker tramite il suo ID.
router.get("/{broker_id}", response_model=BrokerRead, summary="Get a broker by ID")(
    broker_controller.get_broker_by_id
)

# Rotta per aggiornare un broker esistente (accessibile solo agli admin).
router.put(
    "/{broker_id}",
    response_model=BrokerRead,
    summary="Update a broker (admin only)",
    dependencies=[Depends(require_roles(["admin"]))],
)(broker_controller.update_broker)

# Rotta per eliminare un broker (accessibile solo agli admin).
router.delete(
    "/{broker_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a broker (admin only)",
    dependencies=[Depends(require_roles(["admin"]))],
)(broker_controller.delete_broker)

# Rotta per ottenere le classi di asset associate a un broker (admin only).
router.get(
    "/{broker_id}/asset-classes",
    response_model=List[AssetClassRead],
    summary="Get associated asset classes for a broker (admin only)",
    dependencies=[Depends(require_roles(["admin"]))],
)(broker_controller.get_associated_asset_classes)

# Rotta per associare una classe di asset a un broker (admin only).
router.post(
    "/{broker_id}/asset-classes",
    response_model=BrokerAssetClassRead,
    status_code=status.HTTP_201_CREATED,
    summary="Associate an asset class with a broker (admin only)",
    dependencies=[Depends(require_roles(["admin"]))],
)(broker_controller.add_asset_class_to_broker)

# Rotta per disassociare una classe di asset da un broker (admin only).
router.delete(
    "/{broker_id}/asset-classes/{asset_class_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Disassociate an asset class from a broker (admin only)",
    dependencies=[Depends(require_roles(["admin"]))],
)(broker_controller.remove_asset_class_from_broker)