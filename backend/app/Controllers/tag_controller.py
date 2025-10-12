from __future__ import annotations
from typing import List
from uuid import UUID
from fastapi import Depends, HTTPException, status
from app.Services.tag_service import TagService
from app.Services.tags_group_service import TagsGroupService
from app.Schemas.tag import TagCreate, TagRead, TagUpdate
from app.Router.dependencies import get_current_user, get_current_general_account_id, CurrentUser


class TagController:
    def __init__(self) -> None:
        pass

    async def list_my_tags(
        self,
        general_account_id: UUID = Depends(get_current_general_account_id),
        service: TagService = Depends(),
    ) -> List[TagRead]:
        """
        Lista tutti i tag dell'utente autenticato.
        """
        repo = service.repo
        tags = await repo.list_tags_by_general_account_id(general_account_id)
        return [TagRead.from_orm(t) for t in tags]

    async def get_tag(
        self,
        tag_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        service: TagService = Depends(),
    ) -> TagRead:
        """
        Recupera un singolo tag per ID, verificando la proprietà.
        """
        tag = await service.get_tag_by_id(tag_id)

        if not tag.group or (not current_user.is_admin and tag.group.general_account_id != general_account_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accesso non autorizzato.")

        return TagRead.from_orm(tag)

    async def create_tag(
        self,
        tag_data: TagCreate,
        general_account_id: UUID = Depends(get_current_general_account_id),
        tag_service: TagService = Depends(),
        tags_group_service: TagsGroupService = Depends(),
    ) -> TagRead:
        """
        Crea un nuovo tag per l'utente autenticato.
        """
        await tags_group_service.get_tags_group_by_id(
            tag_data.group_id, general_account_id
        )

        new_tag = await tag_service.create_tag(tag_data)
        return TagRead.from_orm(new_tag)

    async def update_tag(
        self,
        tag_id: UUID,
        tag_data: TagUpdate,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        service: TagService = Depends(),
    ) -> TagRead:
        """
        Aggiorna un tag, verificando la proprietà.
        """
        tag_to_update = await service.get_tag_by_id(tag_id)

        if not tag_to_update.group or (not current_user.is_admin and tag_to_update.group.general_account_id != general_account_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accesso non autorizzato.")

        updated_tag = await service.update_tag(db_obj=tag_to_update, tag_data=tag_data)
        if not updated_tag:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Errore durante l'aggiornamento del tag.")

        return TagRead.from_orm(updated_tag)

    async def delete_tag(
        self,
        tag_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        service: TagService = Depends(),
    ) -> dict:
        """
        Elimina un tag, verificando la proprietà.
        """
        tag_to_delete = await service.get_tag_by_id(tag_id)

        if not tag_to_delete.group or (not current_user.is_admin and tag_to_delete.group.general_account_id != general_account_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accesso non autorizzato.")

        await service.delete_tag(db_obj=tag_to_delete)

        return {"ok": True, "detail": "Tag eliminato con successo."}