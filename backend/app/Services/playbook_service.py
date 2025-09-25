# app/Services/playbook_service.py
from uuid import UUID
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Models.auth_user import AuthUser
from app.Repositories.playbook_repository import PlaybookRepository
from app.Repositories.auth_user_repository import AuthUserRepository
from app.Schemas.playbook import PlaybookCreate, PlaybookUpdate, PlaybookRead

class PlaybookService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
        self.repo = PlaybookRepository(db)
        self.user_repo = AuthUserRepository(db)

    async def _get_user_and_validate_ga(self, claims: dict) -> AuthUser:
        """Helper per ottenere l'utente e validare il suo General Account."""
        user_id_str = claims.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token non valido (sub mancante).")

        current_user = await self.user_repo.get(UUID(user_id_str))

        if not current_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utente non trovato.")

        if not current_user.general_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="General Account non trovato per l'utente corrente.",
            )
        return current_user

    async def get_playbooks_by_general_account(self, claims: dict) -> list[PlaybookRead]:
        """Recupera tutti i playbook per il General Account dell'utente autenticato."""
        current_user = await self._get_user_and_validate_ga(claims)
        general_account_id = current_user.general_account.id
        playbooks = await self.repo.list_by_general_account_id(general_account_id=general_account_id)
        return [PlaybookRead.from_orm(p) for p in playbooks]

    async def create_playbook(self, playbook_in: PlaybookCreate, claims: dict) -> PlaybookRead:
        """Crea un nuovo playbook per il General Account dell'utente autenticato."""
        current_user = await self._get_user_and_validate_ga(claims)
        general_account_id = current_user.general_account.id
        playbook = await self.repo.create(playbook_in=playbook_in, general_account_id=general_account_id)
        return PlaybookRead.from_orm(playbook)

    async def update_playbook(self, playbook_id: UUID, playbook_in: PlaybookUpdate, claims: dict) -> PlaybookRead:
        """Aggiorna un playbook, verificando che appartenga al General Account dell'utente."""
        current_user = await self._get_user_and_validate_ga(claims)
        db_playbook = await self.repo.get_by_id(playbook_id)

        if not db_playbook:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playbook non trovato.")

        if db_playbook.general_account_id != current_user.general_account.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non autorizzato a modificare questo playbook.")

        updated_playbook = await self.repo.update(db_obj=db_playbook, obj_in=playbook_in)
        return PlaybookRead.from_orm(updated_playbook)

    async def delete_playbook(self, playbook_id: UUID, claims: dict) -> None:
        """Elimina un playbook, verificando che appartenga al General Account dell'utente."""
        current_user = await self._get_user_and_validate_ga(claims)
        db_playbook = await self.repo.get_by_id(playbook_id)

        if not db_playbook:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playbook non trovato.")

        if db_playbook.general_account_id != current_user.general_account.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non autorizzato a eliminare questo playbook.")

        await self.repo.delete(db_obj=db_playbook)
        return None