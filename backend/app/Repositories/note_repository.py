# app/Repositories/note_repository.py
from __future__ import annotations

from datetime import date
from typing import Sequence
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.Models.note import Note
from app.Models.notebook_folder import NotebookFolder
from app.Models.trade import Trade
from app.Models.note_template import NoteTemplate
from app.Schemas.notebook import NoteCreate, NoteUpdate


class NoteRepository:
    """Repository for Note CRUD operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ------------------------
    # Loading options (eager)
    # ------------------------
    def _get_note_load_options(self):
        """
        Centralized eager loading.
        Mantenuto come joined/selectin per evitare N+1 e rispettare le relazioni many.
        """
        return [
            joinedload(Note.folder),
            joinedload(Note.trade).options(
                joinedload(Trade.asset),
                selectinload(Trade.tags),
                selectinload(Trade.mistakes),
                joinedload(Trade.playbook),
                selectinload(Trade.news_impacts),
                selectinload(Trade.psychology_states),
                selectinload(Trade.rules_followed),
            ),
            selectinload(Note.templates),
        ]

    # ------------------------
    # Helpers per predicate
    # ------------------------
    @staticmethod
    def _not_deleted_note():
        """Predicate per sfruttare gli indici parziali su notes (deleted_at IS NULL)."""
        return Note.deleted_at.is_(None)

    @staticmethod
    def _not_deleted_folder():
        """Predicate per sfruttare gli indici parziali su notebook_folders (deleted_at IS NULL)."""
        return NotebookFolder.deleted_at.is_(None)

    # ------------------------
    # Reads
    # ------------------------
    async def get_by_id(self, note_id: UUID) -> Note | None:
        """
        Get a note by its ID, including related folder, trade, and sub-relationships.
        Filtra anche deleted_at per aderire ai parziali ed evitare di mostrare note soft-deleted.
        """
        stmt = (
            select(Note)
            .options(*self._get_note_load_options())
            .where(Note.id == note_id, self._not_deleted_note())
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().first()

    async def find_by_date_and_folder(self, note_date: date, folder_id: UUID) -> Note | None:
        """
        Find a note by date within a specific folder.
        Indici sfruttati:
        - notes (folder_id, note_date) WHERE deleted_at IS NULL
        """
        stmt = select(Note).where(
            Note.note_date == note_date,
            Note.folder_id == folder_id,
            self._not_deleted_note(),
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def find_by_date_and_general_account(
        self, note_date: date, general_account_id: UUID
    ) -> Note | None:
        """
        Find a note by date for a specific general account.
        Indici sfruttati:
        - notebook_folders (general_account_id) WHERE deleted_at IS NULL
        - notes (note_date) WHERE deleted_at IS NULL
        """
        stmt = (
            select(Note)
            .join(Note.folder)
            .where(
                Note.note_date == note_date,
                NotebookFolder.general_account_id == general_account_id,
                self._not_deleted_note(),
                self._not_deleted_folder(),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def find_by_date_range_and_general_account(
        self, start_date: date, end_date: date, general_account_id: UUID
    ) -> dict[date, Note]:
        """
        Find notes by date range for a specific general account, returned as a dict keyed by date.
        Indici sfruttati:
        - notebook_folders (general_account_id) WHERE deleted_at IS NULL
        - notes (note_date) WHERE deleted_at IS NULL
        - join su folder_id (coperto da idx_notes_folder_id parziale)
        """
        stmt = (
            select(Note)
            .join(Note.folder)
            .where(
                Note.note_date >= start_date,
                Note.note_date <= end_date,
                NotebookFolder.general_account_id == general_account_id,
                self._not_deleted_note(),
                self._not_deleted_folder(),
            )
        )
        result = await self.db.execute(stmt)
        notes = result.scalars().all()
        return {n.note_date: n for n in notes if n.note_date is not None}

    async def get_by_trade_id(self, trade_id: UUID, general_account_id: UUID) -> Note | None:
        """
        Get a note by its trade_id and verify ownership via general_account_id.
        Includes eager loading for related entities.
        Indici sfruttati:
        - notes (trade_id) UNIQUE
        - notebook_folders (general_account_id) WHERE deleted_at IS NULL
        """
        stmt = (
            select(Note)
            .join(Note.folder)
            .options(*self._get_note_load_options())
            .where(
                Note.trade_id == trade_id,
                NotebookFolder.general_account_id == general_account_id,
                self._not_deleted_note(),
                self._not_deleted_folder(),
            )
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().first()

    async def list_by_folder_id(self, folder_id: UUID) -> Sequence[Note]:
        """
        List all notes for a given folder, including related trades and sub-relationships.
        Ordinate per updated_at DESC (indice composito: folder_id, updated_at DESC).
        """
        stmt = (
            select(Note)
            .options(*self._get_note_load_options())
            .where(Note.folder_id == folder_id, self._not_deleted_note())
            .order_by(Note.updated_at.desc().nullslast())
        )
        res = await self.db.execute(stmt)
        return res.unique().scalars().all()

    async def list_by_general_account_id(self, general_account_id: UUID) -> Sequence[Note]:
        """
        List all notes for a given general account by joining through folders,
        including related trades and sub-relationships.
        """
        stmt = (
            select(Note)
            .join(Note.folder)
            .options(*self._get_note_load_options())
            .where(
                NotebookFolder.general_account_id == general_account_id,
                self._not_deleted_note(),
                self._not_deleted_folder(),
            )
            .order_by(Note.updated_at.desc().nullslast())
        )
        res = await self.db.execute(stmt)
        return res.unique().scalars().all()

    # ------------------------
    # Mutations
    # ------------------------
    async def create(self, note_in: NoteCreate) -> Note:
        """Create a new note."""
        db_note = Note(**note_in.model_dump())
        self.db.add(db_note)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            # trade_id è UNIQUE su notes → conflitti di deduplica
            raise HTTPException(
                status_code=409,
                detail="A note for this trade already exists.",
            )

        # Refresh the instance to get server-side defaults (like created_at)
        await self.db.refresh(db_note)
        return db_note

    async def update(self, db_obj: Note, obj_in: NoteUpdate) -> Note:
        """Update an existing note."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        self.db.add(db_obj)
        try:
            await self.db.flush()
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status_code=409,
                detail="A note with this trade_id already exists.",
            )

        # Refresh the instance to get the updated timestamp
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: Note) -> None:
        """
        Delete a note (hard delete).
        Se utilizzi soft-delete a livello applicativo, questo metodo va usato con cautela.
        """
        await self.db.delete(db_obj)
        await self.db.commit()

    # ------------------------
    # Note <-> Template links
    # ------------------------
    async def add_template_to_note(self, note: Note, template: NoteTemplate) -> Note:
        """Associate a note template with a note."""
        note.templates.append(template)
        self.db.add(note)
        await self.db.commit()
        await self.db.refresh(note)
        return note

    async def remove_template_from_note(self, note: Note, template: NoteTemplate) -> Note:
        """Disassociate a note template from a note."""
        note.templates.remove(template)
        self.db.add(note)
        await self.db.commit()
        await self.db.refresh(note)
        return note
