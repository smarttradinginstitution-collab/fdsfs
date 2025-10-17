# app/Controllers/mistake_controller.py
from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Repositories.mistake_repository import MistakeRepository
from app.Schemas.mistake import MistakeCreate, MistakeRead, MistakeUpdate, MistakeAdminRead
from app.Router.dependencies import get_current_user, get_current_general_account_id, CurrentUser


class MistakeController:
    def __init__(self) -> None:
        pass

    async def list_all_mistakes_for_admin(
        self,
        db: AsyncSession = Depends(get_db),
    ) -> List[MistakeAdminRead]:
        """
        [Admin] Lista tutti i mistakes, raggruppati per General Account.
        """
        repo = MistakeRepository(db)
        accounts = await repo.list_all_mistakes_grouped_by_account()

        response_data = []
        for acc in accounts:
            if acc.user:  # Assicura che ci sia un utente associato
                response_data.append(
                    MistakeAdminRead(
                        general_account_id=acc.id,
                        user_email=acc.user.email,
                        mistakes=[MistakeRead.model_validate(m) for m in acc.mistakes],
                    )
                )
        return response_data

    async def list_my_mistakes(
        self,
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> List[MistakeRead]:
        """
        Lista tutti i mistakes dell'utente autenticato.
        """
        repo = MistakeRepository(db)
        mistakes = await repo.list_by_general_account_id(general_account_id)
        return [MistakeRead.model_validate(m) for m in mistakes]

    async def get_mistake(
        self,
        mistake_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> MistakeRead:
        """
        Recupera un singolo mistake per ID, verificando la proprietà.
        """
        repo = MistakeRepository(db)
        mistake = await repo.get_by_id(mistake_id)

        if not mistake:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mistake non trovato.")

        if not current_user.is_admin and mistake.general_account_id != general_account_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accesso non autorizzato.")

        return MistakeRead.model_validate(mistake)

    async def create_mistake(
        self,
        mistake_data: MistakeCreate,
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> MistakeRead:
        """
        Crea un nuovo mistake per l'utente autenticato.
        """
        repo = MistakeRepository(db)
        new_mistake = await repo.create(mistake_in=mistake_data, general_account_id=general_account_id)
        return MistakeRead.model_validate(new_mistake)

    async def update_mistake(
        self,
        mistake_id: UUID,
        mistake_data: MistakeUpdate,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> MistakeRead:
        """
        Aggiorna un mistake, verificando la proprietà.
        """
        repo = MistakeRepository(db)
        mistake_to_update = await repo.get_by_id(mistake_id)

        if not mistake_to_update:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mistake non trovato.")

        if not current_user.is_admin and mistake_to_update.general_account_id != general_account_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accesso non autorizzato.")

        updated_mistake = await repo.update(db_obj=mistake_to_update, obj_in=mistake_data)
        if not updated_mistake:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Errore durante l'aggiornamento del mistake."
            )

        return MistakeRead.model_validate(updated_mistake)

    async def delete_mistake(
        self,
        mistake_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> dict:
        """
        Elimina un mistake, verificando la proprietà.
        """
        repo = MistakeRepository(db)
        mistake_to_delete = await repo.get_by_id(mistake_id)

        if not mistake_to_delete:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mistake non trovato.")

        if not current_user.is_admin and mistake_to_delete.general_account_id != general_account_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accesso non autorizzato.")

        await repo.delete(db_obj=mistake_to_delete)

        return {"ok": True, "detail": "Mistake eliminato con successo."}