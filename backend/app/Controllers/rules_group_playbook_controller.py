# app/Controllers/rules_group_playbook_controller.py
from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Repositories.rules_group_playbook_repository import RulesGroupPlaybookRepository
from app.Repositories.playbook_repository import PlaybookRepository
from app.Schemas.rules_group_playbook import RulesGroupCreate, RulesGroupRead, RulesGroupUpdate
from app.Router.dependencies import get_current_user, get_current_general_account_id, CurrentUser


class RulesGroupPlaybookController:
    def __init__(self) -> None:
        pass

    async def _get_playbook_and_verify_ownership(
        self,
        playbook_id: UUID,
        current_user: CurrentUser,
        general_account_id: UUID,
        db: AsyncSession
    ):
        playbook_repo = PlaybookRepository(db)
        playbook = await playbook_repo.get_by_id(playbook_id)
        if not playbook:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playbook non trovato.")
        if not current_user.is_admin and playbook.general_account_id != general_account_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accesso non autorizzato al playbook.")
        return playbook

    async def list_groups_for_playbook(
        self,
        playbook_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> List[RulesGroupRead]:
        """
        Lista tutti i gruppi di regole per un dato playbook, verificando la proprietà.
        """
        await self._get_playbook_and_verify_ownership(playbook_id, current_user, general_account_id, db)

        repo = RulesGroupPlaybookRepository(db)
        groups = await repo.list_by_playbook_id(playbook_id)
        return [RulesGroupRead.from_orm(g) for g in groups]

    async def create_group_for_playbook(
        self,
        playbook_id: UUID,
        group_data: RulesGroupCreate,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> RulesGroupRead:
        """
        Crea un nuovo gruppo di regole per un playbook, verificando la proprietà.
        """
        if playbook_id != group_data.playbook_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="L'ID del playbook nel path e nel body non corrispondono.")

        await self._get_playbook_and_verify_ownership(playbook_id, current_user, general_account_id, db)

        repo = RulesGroupPlaybookRepository(db)
        new_group = await repo.create(group_in=group_data)
        return RulesGroupRead.from_orm(new_group)

    async def update_group(
        self,
        group_id: UUID,
        group_data: RulesGroupUpdate,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> RulesGroupRead:
        """
        Aggiorna un gruppo di regole, verificando la proprietà tramite il playbook associato.
        """
        repo = RulesGroupPlaybookRepository(db)
        group_to_update = await repo.get_by_id(group_id)

        if not group_to_update:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gruppo di regole non trovato.")

        await self._get_playbook_and_verify_ownership(group_to_update.playbook_id, current_user, general_account_id, db)

        updated_group = await repo.update(db_obj=group_to_update, obj_in=group_data)
        return RulesGroupRead.from_orm(updated_group)

    async def delete_group(
        self,
        group_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> dict:
        """
        Elimina un gruppo di regole, verificando la proprietà.
        """
        repo = RulesGroupPlaybookRepository(db)
        group_to_delete = await repo.get_by_id(group_id)

        if not group_to_delete:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gruppo di regole non trovato.")

        await self._get_playbook_and_verify_ownership(group_to_delete.playbook_id, current_user, general_account_id, db)

        await repo.delete(db_obj=group_to_delete)
        return {"ok": True, "detail": "Gruppo di regole eliminato con successo."}