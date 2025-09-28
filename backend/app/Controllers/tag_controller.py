from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Repositories.tag_repository import TagRepository
from app.Schemas.tag import TagCreate, TagRead, TagUpdate, TagAdminRead
from app.Router.dependencies import get_current_user, get_current_general_account_id, CurrentUser


class TagController:
    def __init__(self) -> None:
        pass

    async def list_all_tags_for_admin(
        self,
        db: AsyncSession = Depends(get_db),
    ) -> List[TagAdminRead]:
        """
        [Admin] Lista tutti i tag, raggruppati per General Account.
        """
        repo = TagRepository(db)
        accounts = await repo.list_all_tags_grouped_by_account()

        response_data = []
        for acc in accounts:
            if acc.user: # Assicura che ci sia un utente associato
                response_data.append(
                    TagAdminRead(
                        general_account_id=acc.id,
                        user_email=acc.user.email,
                        tags=[TagRead.from_orm(t) for t in acc.tags]
                    )
                )
        return response_data

    async def list_my_tags(
        self,
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> List[TagRead]:
        """
        Lista tutti i tag dell'utente autenticato.
        """
        repo = TagRepository(db)
        tags = await repo.list_tags_by_general_account_id(general_account_id)
        return [TagRead.from_orm(t) for t in tags]

    async def get_tag(
        self,
        tag_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> TagRead:
        """
        Recupera un singolo tag per ID, verificando la proprietà.
        """
        repo = TagRepository(db)
        tag = await repo.get_tag_by_id(tag_id)

        if not tag:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag non trovato.")

        # Verifica ownership (o se l'utente è admin)
        if not current_user.is_admin and tag.general_account_id != general_account_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accesso non autorizzato.")

        return TagRead.from_orm(tag)

    async def create_tag(
        self,
        tag_data: TagCreate,
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> TagRead:
        """
        Crea un nuovo tag per l'utente autenticato.
        """
        repo = TagRepository(db)
        new_tag = await repo.create_tag(general_account_id, tag_data)
        return TagRead.from_orm(new_tag)

    async def update_tag(
        self,
        tag_id: UUID,
        tag_data: TagUpdate,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> TagRead:
        """
        Aggiorna un tag, verificando la proprietà.
        """
        repo = TagRepository(db)
        tag_to_update = await repo.get_tag_by_id(tag_id)

        if not tag_to_update:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag non trovato.")

        # Verifica ownership (o se l'utente è admin)
        if not current_user.is_admin and tag_to_update.general_account_id != general_account_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accesso non autorizzato.")

        updated_tag = await repo.update_tag(tag_id, tag_data)
        if not updated_tag:
            # Questo caso può verificarsi se l'update non restituisce nulla, anche se dovrebbe.
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Errore durante l'aggiornamento del tag.")

        return TagRead.from_orm(updated_tag)

    async def delete_tag(
        self,
        tag_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> dict:
        """
        Elimina un tag, verificando la proprietà.
        """
        repo = TagRepository(db)
        tag_to_delete = await repo.get_tag_by_id(tag_id)

        if not tag_to_delete:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag non trovato.")

        # Verifica ownership (o se l'utente è admin)
        if not current_user.is_admin and tag_to_delete.general_account_id != general_account_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accesso non autorizzato.")

        success = await repo.delete_tag_by_id(tag_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Errore durante l'eliminazione del tag.")

        return {"ok": True, "detail": "Tag eliminato con successo."}