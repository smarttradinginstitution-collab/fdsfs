import datetime
from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.Repositories.discipline.discipline_rule_repository import DisciplineRuleRepository
from app.Repositories.discipline.daily_rule_instance_repository import DailyRuleInstanceRepository
from app.Repositories.trade_repository import TradeRepository
from app.Repositories.note_repository import NoteRepository
from app.Repositories.notebook_folder_repository import NotebookFolderRepository
from app.Models.discipline_rule import DisciplineRule
from app.Models.daily_rule_instance import DailyRuleInstance
from app.Schemas.notebook import NoteCreate

class DisciplineService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.rule_repo = DisciplineRuleRepository(db)
        self.instance_repo = DailyRuleInstanceRepository(db)
        self.trade_repo = TradeRepository(db)
        self.note_repo = NoteRepository(db)
        self.folder_repo = NotebookFolderRepository(db)

    async def get_or_create_daily_checklist(self, general_account_id: UUID, trading_account_id: UUID) -> list[DailyRuleInstance]:
        today = datetime.date.today()

        # 1. Find the dedicated "Daily Journal" folder
        daily_journal_folder = await self.folder_repo.find_by_name_and_account("Daily Journal", general_account_id)
        if not daily_journal_folder:
            # Or create it if it doesn't exist
            from app.Schemas.notebook import NotebookFolderCreate
            folder_create_schema = NotebookFolderCreate(name="Daily Journal", folder_type='default')
            daily_journal_folder = await self.folder_repo.create(folder_create_schema, general_account_id)

        # 2. Check if a note for today already exists in that folder
        # This part needs a new repository method: find_by_date_and_folder
        daily_note = await self.note_repo.find_by_date_and_folder(today, daily_journal_folder.id)

        if not daily_note:
            # 3. If no note, create one
            note_schema = NoteCreate(
                folder_id=daily_journal_folder.id,
                title=f"Journal del {today.strftime('%Y-%m-%d')}",
                note_date=today,
                content={"blocks": []} # Empty content
            )
            daily_note = await self.note_repo.create(note_schema)

            # 4. Get all rule templates and create instances for the new note
            rules = await self.rule_repo.list_by_general_account(general_account_id)
            instances_to_create = []
            for rule in rules:
                # Check if the rule is active for the current day of the week
                if today.weekday() in rule.active_days:
                    instances_to_create.append({
                        "daily_journal_id": daily_note.id,
                        "rule_template_id": rule.id,
                        "name": rule.name,
                        "rule_type": rule.rule_type,
                        "status": "pending"
                    })

            if instances_to_create:
                await self.instance_repo.create_many(instances_to_create)

        # 5. Evaluate automated rules for the day
        await self.evaluate_automated_rules(daily_note.id, trading_account_id, today)

        # 6. Return all instances for the daily note
        return await self.instance_repo.find_by_journal_and_date(daily_note.id)

    async def evaluate_automated_rules(self, daily_journal_id: UUID, trading_account_id: UUID, date: datetime.date):
        instances = await self.instance_repo.find_by_journal_and_date(daily_journal_id)
        trades_today = await self.trade_repo.get_filtered_trades(trading_account_id, date, date)

        for instance in instances:
            if instance.rule_type == 'AUTOMATED':
                rule_template = await self.rule_repo.get_by_id(instance.rule_template_id)
                if not rule_template:
                    continue

                is_completed = self._check_rule(rule_template, trades_today)

                new_status = "completed" if is_completed else "failed"
                await self.instance_repo.update(instance.id, {"status": new_status})


    def _check_rule(self, rule: DisciplineRule, trades: list) -> bool:
        # This is a simplified placeholder for the rule evaluation logic
        if rule.name == "Max loss per day":
            total_pnl = sum(trade.p_l for trade in trades if trade.p_l is not None)
            max_loss = float(rule.condition_value.get("amount", 0))
            return total_pnl >= -max_loss
        if rule.name == "Max loss per trade":
            return all(trade.p_l >= -float(rule.condition_value.get("amount", 0)) for trade in trades if trade.p_l is not None)
        if rule.name == "Trade has stop loss":
            return all(trade.stop_loss_price is not None for trade in trades)
        if rule.name == "Link trades to playbook":
            return all(trade.playbook_id is not None for trade in trades)
        if rule.name == "Start my day by 12:00":
            # This rule would be checked when the user first opens the page
            # For now, we'll just return true
            return True
        return False

    async def update_manual_rule_status(self, instance_id: UUID, status: str) -> Optional[DailyRuleInstance]:
        instance = await self.instance_repo.get_by_id(instance_id)
        if instance and instance.rule_type == 'MANUAL':
            return await self.instance_repo.update(instance_id, {"status": status})
        return None

    async def get_heatmap_data(self, general_account_id: UUID, year: int, month: int) -> list[dict]:
        import calendar
        from collections import defaultdict

        # 1. Get the date range for the given month
        _, num_days = calendar.monthrange(year, month)
        start_date = datetime.date(year, month, 1)
        end_date = datetime.date(year, month, num_days)

        # 2. Fetch all relevant rule instances and their dates for the month
        instance_date_tuples = await self.instance_repo.find_by_account_and_date_range(general_account_id, start_date, end_date)

        # 3. Group instances by date
        instances_by_date = defaultdict(list)
        for instance, note_date in instance_date_tuples:
            instances_by_date[note_date].append(instance)

        # 4. Calculate score for each day
        heatmap_data = []
        for day, day_instances in instances_by_date.items():
            if not day_instances:
                continue

            completed_count = sum(1 for i in day_instances if i.status == 'completed')
            total_count = len(day_instances)
            score = (completed_count / total_count) if total_count > 0 else 0.0

            heatmap_data.append({"date": day, "score": score})

        return heatmap_data