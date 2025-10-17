# backend/app/Services/journal_service.py
from __future__ import annotations
from uuid import UUID
from datetime import date, datetime
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Repositories.note_repository import NoteRepository
from app.Repositories.notebook_folder_repository import NotebookFolderRepository
from app.Repositories.discipline_rule_repository import DisciplineRuleRepository
from sqlalchemy import func
from app.Repositories.daily_rule_instance_repository import DailyRuleInstanceRepository
from app.Repositories.general_account_repository import GeneralAccountRepository
from app.Repositories.trade_repository import TradeRepository
from app.Models.notebook_folder import SystemFolderIdentifier
from app.Models.trade import Trade
from app.Schemas.journal import JournalDay
from app.Schemas.notebook import NoteCreate
from app.Schemas.daily_rule_instance import DailyRuleInstanceRead


class JournalService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
        self.note_repo = NoteRepository(db)
        self.folder_repo = NotebookFolderRepository(db)
        self.rule_repo = DisciplineRuleRepository(db)
        self.instance_repo = DailyRuleInstanceRepository(db)
        self.general_account_repo = GeneralAccountRepository(db)
        self.trade_repo = TradeRepository(db)

    async def _get_general_account_id(self, user_id: UUID) -> UUID:
        general_account = await self.general_account_repo.get_by_user_id(user_id)
        if not general_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="General Account not found.",
            )
        return general_account.id

    async def start_day(self, claims: dict, day: date) -> JournalDay:
        user_id = UUID(claims["sub"])
        general_account_id = await self._get_general_account_id(user_id)

        # 1. Find the "Daily Journal" folder
        daily_journal_folder = await self.folder_repo.get_by_system_identifier(
            general_account_id, SystemFolderIdentifier.DAILY_JOURNAL
        )
        if not daily_journal_folder:
            # Or create it if it doesn't exist
            daily_journal_folder = await self.folder_repo.create_system_folder(
                general_account_id,
                "Daily Journal",
                SystemFolderIdentifier.DAILY_JOURNAL,
            )

        # 2. Check if a note for this day already exists
        existing_note = await self.note_repo.get_daily_journal_by_date(
            general_account_id, day
        )
        if existing_note:
            # If it exists, just return the data for that day
            return await self.get_day(claims, day)

        # 3. Create a new note
        note_create = NoteCreate(
            folder_id=daily_journal_folder.id,
            title=f"Journal - {day.strftime('%Y-%m-%d')}",
            content={"type": "doc", "content": []}, # Default empty content
            note_date=day,
        )
        new_note = await self.note_repo.create(note_create)

        # 4. Get active rules for the day of the week
        weekday = day.weekday()  # Monday is 0 and Sunday is 6
        all_rules = await self.rule_repo.list_by_general_account_id(general_account_id)
        active_rules = [rule for rule in all_rules if weekday in rule.active_days]

        # 5. Create daily rule instances
        instances_to_create = []
        for rule in active_rules:
            instances_to_create.append(
                {
                    "daily_journal_id": new_note.id,
                    "rule_template_id": rule.id,
                    "name": rule.name,
                    "rule_type": rule.rule_type,
                }
            )

        if instances_to_create:
            await self.instance_repo.create_many(instances_to_create)

        return await self.get_day(claims, day)

    async def get_day(self, claims: dict, day: date) -> JournalDay:
        user_id = UUID(claims["sub"])
        general_account_id = await self._get_general_account_id(user_id)

        note = await self.note_repo.get_daily_journal_by_date(general_account_id, day)
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Journal for this day not found. Use 'start-day' first."
            )

        # Evaluate automated rules
        trades_today = await self.trade_repo.get_trades_by_day(general_account_id, day)
        for instance in note.daily_rule_instances:
            if instance.rule_type == "AUTOMATED":
                rule = await self.rule_repo.get_by_id(instance.rule_template_id, general_account_id)
                if rule:
                    # This is a simplified example. A real implementation would have a
                    # factory or strategy pattern to handle different rule conditions.
                    if rule.condition_type == "MAX_LOSS_PER_DAY":
                        total_loss = sum(t.p_l for t in trades_today if t.p_l < 0)
                        if abs(total_loss) > rule.condition_value["amount"]:
                            instance.status = "failed"
                        else:
                            instance.status = "completed"
                        instance.actual_value = f"${abs(total_loss)} / ${rule.condition_value['amount']}"

        # Calculate P/L for the day
        pnl = sum(t.p_l for t in trades_today)

        return JournalDay(
            note=note,
            rules=note.daily_rule_instances,
            pnl=pnl,
        )

    async def update_manual_rule_status(self, claims: dict, instance_id: UUID, status: str) -> DailyRuleInstanceRead:
        user_id = UUID(claims["sub"])
        general_account_id = await self._get_general_account_id(user_id)

        instance = await self.instance_repo.get_by_id(instance_id)
        if not instance:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Rule instance not found")

        # Security check: Ensure the instance belongs to the user
        note = await self.note_repo.get_by_id(instance.daily_journal_id)
        if not note or note.folder.general_account_id != general_account_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You do not have permission to update this rule.")

        if instance.rule_type != "MANUAL":
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only manual rules can be updated this way.")

        instance.status = status
        await self.instance_repo.commit_and_refresh(instance)

        return DailyRuleInstanceRead.model_validate(instance)