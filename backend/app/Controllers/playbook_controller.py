# app/Controllers/playbook_controller.py
from uuid import UUID
from fastapi import APIRouter, Depends, status
from typing import List

from app.Schemas.playbook import PlaybookRead, PlaybookCreate, PlaybookUpdate
from app.Services.playbook_service import PlaybookService
from app.Router.auth import get_current_claims

router = APIRouter()

@router.get("/", response_model=List[PlaybookRead], status_code=status.HTTP_200_OK)
async def get_my_playbooks(
    claims: dict = Depends(get_current_claims),
    service: PlaybookService = Depends(PlaybookService)
):
    """
    Recupera tutti i playbook per l'utente autenticato.
    """
    return await service.get_playbooks_by_general_account(claims=claims)

@router.post("/", response_model=PlaybookRead, status_code=status.HTTP_201_CREATED)
async def create_playbook(
    playbook_in: PlaybookCreate,
    claims: dict = Depends(get_current_claims),
    service: PlaybookService = Depends(PlaybookService)
):
    """
    Crea un nuovo playbook.
    """
    return await service.create_playbook(playbook_in=playbook_in, claims=claims)

@router.put("/{playbook_id}", response_model=PlaybookRead, status_code=status.HTTP_200_OK)
async def update_playbook(
    playbook_id: UUID,
    playbook_in: PlaybookUpdate,
    claims: dict = Depends(get_current_claims),
    service: PlaybookService = Depends(PlaybookService)
):
    """
    Aggiorna un playbook esistente.
    """
    return await service.update_playbook(playbook_id=playbook_id, playbook_in=playbook_in, claims=claims)

@router.delete("/{playbook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_playbook(
    playbook_id: UUID,
    claims: dict = Depends(get_current_claims),
    service: PlaybookService = Depends(PlaybookService)
):
    """
    Elimina un playbook.
    """
    await service.delete_playbook(playbook_id=playbook_id, claims=claims)
    return None