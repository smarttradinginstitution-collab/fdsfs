from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Repositories.tag_repository import TagRepository
from app.Repositories.tags_group_repository import TagsGroupRepository
from app.Schemas.tag import TagCreate, TagRead, TagUpdate
from app.Router.dependencies import get_current_user, get_current_general_account_id, CurrentUser


class TagController:
    def __init__(self) -> None:
        pass

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
        if not tag.group or (not current_user.is_admin and tag.group.general_account_id != general_account_id):
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
        # Verify that the group exists and belongs to the user
        tags_group_repo = TagsGroupRepository(db)
        group = await tags_group_repo.get_tags_group_by_id(
            tag_data.group_id, general_account_id
        )
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tags Group not found or access denied.",
            )

        tag_repo = TagRepository(db)
        new_tag = await tag_repo.create_tag(tag_data)
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
        if not tag_to_update.group or (not current_user.is_admin and tag_to_update.group.general_account_id != general_account_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accesso non autorizzato.")

        updated_tag = await repo.update_tag(db_obj=tag_to_update, tag_data=tag_data)
        if not updated_tag:
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
        if not tag_to_delete.group or (not current_user.is_admin and tag_to_delete.group.general_account_id != general_account_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accesso non autorizzato.")

        await repo.delete_tag(db_obj=tag_to_delete)

        return {"ok": True, "detail": "Tag eliminato con successo."}