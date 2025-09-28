# app/Controllers/playbook_controller.py
from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Repositories.playbook_repository import PlaybookRepository
from app.Schemas.playbook import PlaybookCreate, PlaybookRead, PlaybookUpdate
from app.Router.dependencies import get_current_user, get_current_general_account_id, CurrentUser


class PlaybookController:
    def __init__(self) -> None:
        pass

    async def list_my_playbooks(
        self,
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> List[PlaybookRead]:
        """
        Lista tutti i playbook dell'utente autenticato.
        """
        repo = PlaybookRepository(db)
        playbooks = await repo.list_by_general_account_id(general_account_id)
        return [PlaybookRead.from_orm(p) for p in playbooks]

    async def get_playbook(
        self,
        playbook_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> PlaybookRead:
        """
        Recupera un singolo playbook per ID, verificando la proprietà.
        """
        repo = PlaybookRepository(db)
        playbook = await repo.get_by_id(playbook_id)

        if not playbook:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playbook non trovato.")

        if not current_user.is_admin and playbook.general_account_id != general_account_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accesso non autorizzato.")

        return PlaybookRead.from_orm(playbook)

    async def create_playbook(
        self,
        playbook_data: PlaybookCreate,
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> PlaybookRead:
        """
        Crea un nuovo playbook per l'utente autenticato.
        """
        repo = PlaybookRepository(db)
        new_playbook = await repo.create(playbook_in=playbook_data, general_account_id=general_account_id)
        return PlaybookRead.from_orm(new_playbook)

    async def update_playbook(
        self,
        playbook_id: UUID,
        playbook_data: PlaybookUpdate,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> PlaybookRead:
        """
        Aggiorna un playbook, verificando la proprietà.
        """
        repo = PlaybookRepository(db)
        playbook_to_update = await repo.get_by_id(playbook_id)

        if not playbook_to_update:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playbook non trovato.")

        if not current_user.is_admin and playbook_to_update.general_account_id != general_account_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accesso non autorizzato.")

        updated_playbook = await repo.update(db_obj=playbook_to_update, obj_in=playbook_data)
        if not updated_playbook:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Errore durante l'aggiornamento del playbook."
            )

        return PlaybookRead.from_orm(updated_playbook)

    async def delete_playbook(
        self,
        playbook_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> dict:
        """
        Elimina un playbook, verificando la proprietà.
        """
        repo = PlaybookRepository(db)
        playbook_to_delete = await repo.get_by_id(playbook_id)

        if not playbook_to_delete:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playbook non trovato.")

        if not current_user.is_admin and playbook_to_delete.general_account_id != general_account_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accesso non autorizzato.")

        await repo.delete(db_obj=playbook_to_delete)

        return {"ok": True, "detail": "Playbook eliminato con successo."}