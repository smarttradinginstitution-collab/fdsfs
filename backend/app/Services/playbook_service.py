# app/Services/playbook_service.py
from uuid import UUID
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.Models.auth_user import AuthUser
from app.Models.playbook import Playbook
from app.Repositories.playbook_repository import playbook_repository, PlaybookRepository
from app.Repositories.auth_user_repository import AuthUserRepository
from app.Schemas.playbook import PlaybookCreate, PlaybookUpdate
# Rimossa l'importazione di get_current_claims perché non più usata come dipendenza qui

class PlaybookService:
    def __init__(
        self,
        repo: PlaybookRepository = Depends(lambda: playbook_repository),
    ):
        self.repo = repo

    async def _get_user_and_validate_ga(self, db: Session, claims: dict) -> AuthUser:
        """Helper per ottenere l'utente e validare il suo General Account."""
        user_id_str = claims.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token non valido (sub mancante).")

        user_repo = AuthUserRepository(db)
        current_user = await user_repo.get(UUID(user_id_str))

        if not current_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utente non trovato.")

        if not current_user.general_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="General Account non trovato per l'utente corrente.",
            )
        return current_user

    async def get_playbooks_by_general_account(
        self, db: Session, claims: dict
    ) -> list[Playbook]:
        """
        Recupera tutti i playbook per il General Account dell'utente autenticato.
        """
        current_user = await self._get_user_and_validate_ga(db, claims)
        general_account_id = current_user.general_account.id
        return await self.repo.get_by_general_account_id(db, general_account_id=general_account_id)

    async def create_playbook(
        self, playbook_in: PlaybookCreate, db: Session, claims: dict
    ) -> Playbook:
        """
        Crea un nuovo playbook per il General Account dell'utente autenticato.
        """
        current_user = await self._get_user_and_validate_ga(db, claims)
        general_account_id = current_user.general_account.id
        return await self.repo.create(db, playbook_in=playbook_in, general_account_id=general_account_id)

    async def update_playbook(
        self, playbook_id: UUID, playbook_in: PlaybookUpdate, db: Session, claims: dict
    ) -> Playbook:
        """
        Aggiorna un playbook, verificando che appartenga al General Account dell'utente.
        """
        current_user = await self._get_user_and_validate_ga(db, claims)
        db_playbook = await self.repo.get_by_id(db, playbook_id)

        if not db_playbook:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playbook non trovato.")

        if db_playbook.general_account_id != current_user.general_account.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non autorizzato a modificare questo playbook.")

        return await self.repo.update(db, db_obj=db_playbook, obj_in=playbook_in)

    async def delete_playbook(
        self, playbook_id: UUID, db: Session, claims: dict
    ) -> Playbook:
        """
        Elimina un playbook, verificando che appartenga al General Account dell'utente.
        """
        current_user = await self._get_user_and_validate_ga(db, claims)
        db_playbook = await self.repo.get_by_id(db, playbook_id)

        if not db_playbook:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playbook non trovato.")

        if db_playbook.general_account_id != current_user.general_account.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non autorizzato a eliminare questo playbook.")

        return await self.repo.delete(db, db_obj=db_playbook)

playbook_service = PlaybookService()