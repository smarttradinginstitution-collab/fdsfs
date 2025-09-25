# app/Repositories/playbook_repository.py
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from app.Models.playbook import Playbook
from app.Schemas.playbook import PlaybookCreate, PlaybookUpdate

class PlaybookRepository:
    async def get_by_id(self, db: Session, playbook_id: UUID) -> Playbook | None:
        """
        Recupera un playbook per ID.
        """
        result = await db.execute(select(Playbook).filter(Playbook.id == playbook_id))
        return result.scalars().first()

    async def get_by_general_account_id(self, db: Session, general_account_id: UUID) -> list[Playbook]:
        """
        Recupera tutti i playbook associati a un General Account.
        """
        result = await db.execute(select(Playbook).filter(Playbook.general_account_id == general_account_id))
        return result.scalars().all()

    async def create(self, db: Session, playbook_in: PlaybookCreate, general_account_id: UUID) -> Playbook:
        """
        Crea un nuovo playbook.
        """
        db_playbook = Playbook(
            **playbook_in.model_dump(),
            general_account_id=general_account_id
        )
        db.add(db_playbook)
        await db.commit()
        await db.refresh(db_playbook)
        return db_playbook

    async def update(self, db: Session, db_obj: Playbook, obj_in: PlaybookUpdate) -> Playbook:
        """
        Aggiorna un playbook esistente.
        """
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: Session, db_obj: Playbook) -> Playbook:
        """
        Elimina un playbook.
        """
        await db.delete(db_obj)
        await db.commit()
        return db_obj

playbook_repository = PlaybookRepository()