from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Repositories.psychology_state_repository import PsychologyStateRepository
from app.Schemas.psychology_state import PsychologyStateCreate, PsychologyStateRead, PsychologyStateUpdate, PsychologyStateAdminRead
from app.Router.dependencies import get_current_user, get_current_general_account_id, CurrentUser


class PsychologyStateController:
    def __init__(self) -> None:
        pass

    async def list_all_psychology_states_for_admin(
        self,
        db: AsyncSession = Depends(get_db),
    ) -> List[PsychologyStateAdminRead]:
        """
        [Admin] Lista tutti gli stati psicologici, raggruppati per General Account.
        """
        repo = PsychologyStateRepository(db)
        accounts = await repo.list_all_psychology_states_grouped_by_account()

        response_data = []
        for acc in accounts:
            if acc.user: # Assicura che ci sia un utente associato
                response_data.append(
                    PsychologyStateAdminRead(
                        general_account_id=acc.id,
                        user_email=acc.user.email,
                        psychology_states=[PsychologyStateRead.from_orm(ps) for ps in acc.psychology_states]
                    )
                )
        return response_data

    async def list_my_psychology_states(
        self,
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> List[PsychologyStateRead]:
        """
        Lista tutti gli stati psicologici dell'utente autenticato.
        """
        repo = PsychologyStateRepository(db)
        psychology_states = await repo.list_psychology_states_by_general_account_id(general_account_id)
        return [PsychologyStateRead.from_orm(ps) for ps in psychology_states]

    async def get_psychology_state(
        self,
        psychology_state_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> PsychologyStateRead:
        """
        Recupera un singolo stato psicologico per ID, verificando la proprietà.
        """
        repo = PsychologyStateRepository(db)
        psychology_state = await repo.get_psychology_state_by_id(psychology_state_id)

        if not psychology_state:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stato psicologico non trovato.")

        if not current_user.is_admin and psychology_state.general_account_id != general_account_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accesso non autorizzato.")

        return PsychologyStateRead.from_orm(psychology_state)

    async def create_psychology_state(
        self,
        psychology_state_data: PsychologyStateCreate,
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> PsychologyStateRead:
        """
        Crea un nuovo stato psicologico per l'utente autenticato.
        """
        repo = PsychologyStateRepository(db)
        new_psychology_state = await repo.create_psychology_state(general_account_id, psychology_state_data)
        return PsychologyStateRead.from_orm(new_psychology_state)

    async def update_psychology_state(
        self,
        psychology_state_id: UUID,
        psychology_state_data: PsychologyStateUpdate,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> PsychologyStateRead:
        """
        Aggiorna uno stato psicologico, verificando la proprietà.
        """
        repo = PsychologyStateRepository(db)
        psychology_state_to_update = await repo.get_psychology_state_by_id(psychology_state_id)

        if not psychology_state_to_update:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stato psicologico non trovato.")

        if not current_user.is_admin and psychology_state_to_update.general_account_id != general_account_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accesso non autorizzato.")

        updated_psychology_state = await repo.update_psychology_state(db_obj=psychology_state_to_update, psychology_state_data=psychology_state_data)
        if not updated_psychology_state:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Errore durante l'aggiornamento dello stato psicologico.")

        return PsychologyStateRead.from_orm(updated_psychology_state)

    async def delete_psychology_state(
        self,
        psychology_state_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> dict:
        """
        Elimina uno stato psicologico, verificando la proprietà.
        """
        repo = PsychologyStateRepository(db)
        psychology_state_to_delete = await repo.get_psychology_state_by_id(psychology_state_id)

        if not psychology_state_to_delete:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stato psicologico non trovato.")

        if not current_user.is_admin and psychology_state_to_delete.general_account_id != general_account_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accesso non autorizzato.")

        await repo.delete_psychology_state(db_obj=psychology_state_to_delete)

        return {"ok": True, "detail": "Stato psicologico eliminato con successo."}