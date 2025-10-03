# app/Controllers/broker_controller.py
# Questo file contiene la logica di business per la gestione dei broker.
# Non contiene definizioni di rotte (APIRouter), ma solo le funzioni che vengono
# chiamate dagli endpoint definiti nel file di routing corrispondente.
from __future__ import annotations

import uuid

from fastapi import Depends

# Importa i servizi che contengono la logica di interazione con il database.
from app.Services.broker_service import BrokerService
# Importa gli schemi Pydantic per la validazione dei dati.
from app.Schemas.broker import BrokerCreate, BrokerUpdate
from app.Schemas.broker_asset_class import BrokerAssetClassCreate


# ==============================================================================
# FUNZIONI DEL CONTROLLER
# ==============================================================================
# Ogni funzione corrisponde a un'operazione specifica e delega il lavoro
# pesante al BrokerService. L'uso di `Depends()` permette a FastAPI di
# iniettare un'istanza del servizio in ogni chiamata.

async def create_broker(
    broker_data: BrokerCreate,
    service: BrokerService = Depends(),
):
    """
    Crea un nuovo broker.
    - **broker_data**: Dati del broker da creare, validati tramite lo schema Pydantic.
    - **service**: Istanza del BrokerService iniettata da FastAPI.
    """
    # Delega la creazione al servizio.
    return await service.create_broker(broker_data)


async def get_all_brokers(
    service: BrokerService = Depends(),
):
    """
    Recupera la lista di tutti i broker disponibili.
    """
    # Delega il recupero della lista al servizio.
    return await service.get_all_brokers()


async def get_broker_by_id(
    broker_id: uuid.UUID,
    service: BrokerService = Depends(),
):
    """
    Recupera un singolo broker tramite il suo ID.
    """
    # Delega il recupero del singolo broker al servizio.
    return await service.get_broker_by_id(broker_id)


async def update_broker(
    broker_id: uuid.UUID,
    broker_data: BrokerUpdate,
    service: BrokerService = Depends(),
):
    """
    Aggiorna i dati di un broker esistente.
    """
    # Delega l'aggiornamento al servizio.
    return await service.update_broker(broker_id, broker_data)


async def delete_broker(
    broker_id: uuid.UUID,
    service: BrokerService = Depends(),
):
    """
    Elimina un broker tramite il suo ID.
    """
    # Delega l'eliminazione al servizio.
    await service.delete_broker(broker_id)
    # Per le operazioni DELETE, è comune non restituire alcun contenuto.
    return None


async def get_associated_asset_classes(
    broker_id: uuid.UUID,
    service: BrokerService = Depends(),
):
    """
    Recupera le classi di asset associate a un broker specifico.
    """
    # Delega l'operazione al servizio.
    return await service.get_associated_asset_classes(broker_id)


async def add_asset_class_to_broker(
    broker_id: uuid.UUID,
    association_data: BrokerAssetClassCreate,
    service: BrokerService = Depends(),
):
    """
    Associa una classe di asset a un broker.
    """
    # Delega l'associazione al servizio.
    return await service.add_asset_class_to_broker(broker_id, association_data)


async def remove_asset_class_from_broker(
    broker_id: uuid.UUID,
    asset_class_id: uuid.UUID,
    service: BrokerService = Depends(),
):
    """
    Disassocia una classe di asset da un broker.
    """
    # Delega la disassociazione al servizio.
    await service.remove_asset_class_from_broker(broker_id, asset_class_id)
    # Anche in questo caso, non è necessario restituire contenuto.
    return None