# app/Controllers/rule_playbook_controller.py
from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Repositories.rule_playbook_repository import RulePlaybookRepository
from app.Repositories.rules_group_playbook_repository import RulesGroupPlaybookRepository
from app.Repositories.playbook_repository import PlaybookRepository
from app.Schemas.rule_playbook import RuleCreate, RuleRead, RuleUpdate
from app.Router.dependencies import get_current_user, get_current_general_account_id, CurrentUser

class RulePlaybookController:
    def __init__(self) -> None:
        pass

    async def _get_group_and_verify_ownership(
        self,
        group_id: UUID,
        current_user: CurrentUser,
        general_account_id: UUID,
        db: AsyncSession
    ):
        group_repo = RulesGroupPlaybookRepository(db)
        group = await group_repo.get_by_id(group_id)
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gruppo di regole non trovato.")

        playbook_repo = PlaybookRepository(db)
        playbook = await playbook_repo.get_by_id(group.playbook_id)
        if not playbook or (not current_user.is_admin and playbook.general_account_id != general_account_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accesso non autorizzato al gruppo di regole.")

        return group

    async def list_rules_for_group(
        self,
        group_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> List[RuleRead]:
        """
        Lista tutte le regole per un dato gruppo, verificando la proprietà.
        """
        await self._get_group_and_verify_ownership(group_id, current_user, general_account_id, db)

        repo = RulePlaybookRepository(db)
        rules = await repo.list_by_group_id(group_id)
        return [RuleRead.from_orm(r) for r in rules]

    async def create_rule_for_group(
        self,
        group_id: UUID,
        rule_data: RuleCreate,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> RuleRead:
        """
        Crea una nuova regola per un gruppo, verificando la proprietà.
        """
        if group_id != rule_data.rules_groups_playbook_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="L'ID del gruppo nel path e nel body non corrispondono.")

        await self._get_group_and_verify_ownership(group_id, current_user, general_account_id, db)

        repo = RulePlaybookRepository(db)
        new_rule = await repo.create(rule_in=rule_data)
        return RuleRead.from_orm(new_rule)

    async def update_rule(
        self,
        rule_id: UUID,
        rule_data: RuleUpdate,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> RuleRead:
        """
        Aggiorna una regola, verificando la proprietà tramite il gruppo associato.
        """
        repo = RulePlaybookRepository(db)
        rule_to_update = await repo.get_by_id(rule_id)

        if not rule_to_update:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regola non trovata.")

        await self._get_group_and_verify_ownership(rule_to_update.rules_groups_playbook_id, current_user, general_account_id, db)

        updated_rule = await repo.update(db_obj=rule_to_update, obj_in=rule_data)
        return RuleRead.from_orm(updated_rule)

    async def delete_rule(
        self,
        rule_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> dict:
        """
        Elimina una regola, verificando la proprietà.
        """
        repo = RulePlaybookRepository(db)
        rule_to_delete = await repo.get_by_id(rule_id)

        if not rule_to_delete:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regola non trovata.")

        await self._get_group_and_verify_ownership(rule_to_delete.rules_groups_playbook_id, current_user, general_account_id, db)

        await repo.delete(db_obj=rule_to_delete)
        return {"ok": True, "detail": "Regola eliminata con successo."}