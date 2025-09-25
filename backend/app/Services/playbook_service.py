# app/Services/playbook_service.py
from uuid import UUID
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.Models.auth_user import AuthUser
from app.Models.playbook import Playbook
from app.Repositories.playbook_repository import playbook_repository, PlaybookRepository
from app.Schemas.playbook import PlaybookCreate, PlaybookUpdate
from app.Services.auth_service import get_current_user_with_roles

class PlaybookService:
    def __init__(
        self,
        repo: PlaybookRepository = Depends(lambda: playbook_repository),
    ):
        self.repo = repo

    async def get_playbooks_by_general_account(
        self, db: Session, current_user: AuthUser = Depends(get_current_user_with_roles)
    ) -> list[Playbook]:
        """
        Recupera tutti i playbook per il General Account dell'utente autenticato.
        """
        if not current_user.general_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="General Account non trovato per l'utente corrente.",
            )

        general_account_id = current_user.general_account.id
        return self.repo.get_by_general_account_id(db, general_account_id=general_account_id)

    async def create_playbook(
        self, playbook_in: PlaybookCreate, db: Session, current_user: AuthUser = Depends(get_current_user_with_roles)
    ) -> Playbook:
        """
        Crea un nuovo playbook per il General Account dell'utente autenticato.
        """
        if not current_user.general_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="General Account non trovato per l'utente corrente.",
            )

        general_account_id = current_user.general_account.id
        return self.repo.create(db, playbook_in=playbook_in, general_account_id=general_account_id)

    async def update_playbook(
        self, playbook_id: UUID, playbook_in: PlaybookUpdate, db: Session, current_user: AuthUser = Depends(get_current_user_with_roles)
    ) -> Playbook:
        """
        Aggiorna un playbook, verificando che appartenga al General Account dell'utente.
        """
        db_playbook = self.repo.get_by_id(db, playbook_id)
        if not db_playbook:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playbook non trovato.")

        if db_playbook.general_account_id != current_user.general_account.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non autorizzato a modificare questo playbook.")

        return self.repo.update(db, db_obj=db_playbook, obj_in=playbook_in)

    async def delete_playbook(
        self, playbook_id: UUID, db: Session, current_user: AuthUser = Depends(get_current_user_with_roles)
    ) -> Playbook:
        """
        Elimina un playbook, verificando che appartenga al General Account dell'utente.
        """
        db_playbook = self.repo.get_by_id(db, playbook_id)
        if not db_playbook:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playbook non trovato.")

        if db_playbook.general_account_id != current_user.general_account.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non autorizzato a eliminare questo playbook.")

        return self.repo.delete(db, db_obj=db_playbook)

playbook_service = PlaybookService()