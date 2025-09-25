# app/Controllers/playbook_controller.py
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.Schemas.playbook import PlaybookRead, PlaybookCreate, PlaybookUpdate
from app.Services.playbook_service import PlaybookService
from app.Infrastructure.db import get_db

router = APIRouter()

# Istanzia il service una sola volta per evitare di creare un'istanza per ogni richiesta
playbook_service = PlaybookService()

@router.get("/", response_model=List[PlaybookRead], status_code=status.HTTP_200_OK)
async def get_my_playbooks(
    db: Session = Depends(get_db),
    service: PlaybookService = Depends(PlaybookService) # Usa Depends per l'iniezione
):
    """
    Recupera tutti i playbook per l'utente autenticato.
    Questa sarà la rotta principale usata dal frontend.
    """
    # La logica per ottenere l'utente corrente è gestita nel service
    return await service.get_playbooks_by_general_account(db=db)

@router.post("/", response_model=PlaybookRead, status_code=status.HTTP_201_CREATED)
async def create_playbook(
    playbook_in: PlaybookCreate,
    db: Session = Depends(get_db),
    service: PlaybookService = Depends(PlaybookService)
):
    """
    Crea un nuovo playbook.
    """
    return await service.create_playbook(playbook_in=playbook_in, db=db)

@router.put("/{playbook_id}", response_model=PlaybookRead, status_code=status.HTTP_200_OK)
async def update_playbook(
    playbook_id: UUID,
    playbook_in: PlaybookUpdate,
    db: Session = Depends(get_db),
    service: PlaybookService = Depends(PlaybookService)
):
    """
    Aggiorna un playbook esistente.
    """
    return await service.update_playbook(playbook_id=playbook_id, playbook_in=playbook_in, db=db)

@router.delete("/{playbook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_playbook(
    playbook_id: UUID,
    db: Session = Depends(get_db),
    service: PlaybookService = Depends(PlaybookService)
):
    """
    Elimina un playbook.
    """
    await service.delete_playbook(playbook_id=playbook_id, db=db)
    return None # Ritorna una risposta vuota con status 204