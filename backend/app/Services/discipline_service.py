import datetime
from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.Repositories.discipline.discipline_rule_repository import DisciplineRuleRepository
from app.Repositories.discipline.daily_rule_instance_repository import DailyRuleInstanceRepository
from app.Repositories.trade_repository import TradeRepository
from app.Repositories.note_repository import NoteRepository
from app.Repositories.notebook_folder_repository import NotebookFolderRepository
from app.Repositories.trading_account_repository import TradingAccountRepository
from app.Models.discipline_rule import DisciplineRule
from app.Models.daily_rule_instance import DailyRuleInstance
from app.Models.note import Note
from app.Schemas.notebook import NoteCreate

class DisciplineService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.rule_repo = DisciplineRuleRepository(db)
        self.instance_repo = DailyRuleInstanceRepository(db)
        self.trade_repo = TradeRepository(db)
        self.note_repo = NoteRepository(db)
        self.folder_repo = NotebookFolderRepository(db)
        self.trading_account_repo = TradingAccountRepository(db)

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
            # 3. If no note, create one and calculate starting balance

            # Calculate current balance
            trading_account = await self.trading_account_repo.get_by_id(trading_account_id)
            if not trading_account:
                # This should ideally not happen if the ID is validated upstream
                raise Exception("Trading account not found")

            all_trades = await self.trade_repo.get_all_trades_for_account(trading_account_id)
            total_pnl = sum(trade.p_l for trade in all_trades if trade.p_l is not None)
            starting_balance = trading_account.initial_balance + total_pnl

            # Create the daily note with the calculated balance
            note_schema = NoteCreate(
                folder_id=daily_journal_folder.id,
                title=f"Journal del {today.strftime('%Y-%m-%d')}",
                note_date=today,
                content={"blocks": []}, # Empty content
                starting_balance_of_day=starting_balance
            )
            daily_note = await self.note_repo.create(note_schema)

            # 4. Create default rules if they don't exist, then get all rules
            await self._create_default_automated_rules_if_not_exist(general_account_id)
            rules = await self.rule_repo.list_by_general_account(general_account_id)

            # 5. Create instances for the new note
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

        # 6. Evaluate automated rules for the day
        await self.evaluate_automated_rules(daily_note.id, trading_account_id, today)

        # 7. Return all instances for the daily note
        return await self.instance_repo.find_by_journal_and_date(daily_note.id)

    async def _create_default_automated_rules_if_not_exist(self, general_account_id: UUID):
        existing_rules = await self.rule_repo.list_by_general_account(general_account_id)
        automated_rules_exist = any(r.rule_type == 'AUTOMATED' for r in existing_rules)

        if not automated_rules_exist:
            default_rules = [
                {"name": "Start my day by 12:00", "rule_type": "AUTOMATED", "condition_type": "TIME", "condition_value": {"time": "12:00"}, "active_days": [0,1,2,3,4]},
                {"name": "Link trades to playbook", "rule_type": "AUTOMATED", "condition_type": "PERCENTAGE", "condition_value": {"percentage": 100}, "active_days": [0,1,2,3,4]},
                {"name": "Trade has stop loss", "rule_type": "AUTOMATED", "condition_type": "PERCENTAGE", "condition_value": {"percentage": 100}, "active_days": [0,1,2,3,4]},
                {"name": "Max loss per trade", "rule_type": "AUTOMATED", "condition_type": "PERCENTAGE_OR_FIXED", "condition_value": {"amount": 500, "type": "FIXED_AMOUNT"}, "active_days": [0,1,2,3,4]},
                {"name": "Max loss per day", "rule_type": "AUTOMATED", "condition_type": "FIXED_AMOUNT", "condition_value": {"amount": 4000}, "active_days": [0,1,2,3,4]},
            ]
            for rule_data in default_rules:
                rule_data["general_account_id"] = general_account_id
                await self.rule_repo.create(rule_data)

    async def evaluate_automated_rules(self, daily_journal_id: UUID, trading_account_id: UUID, date: datetime.date):
        daily_note = await self.note_repo.get_by_id(daily_journal_id)
        if not daily_note:
            return # Should not happen

        instances = await self.instance_repo.find_by_journal_and_date(daily_journal_id)
        trades_today = await self.trade_repo.get_filtered_trades(trading_account_id, date, date)

        for instance in instances:
            if instance.rule_type == 'AUTOMATED':
                rule_template = await self.rule_repo.get_by_id(instance.rule_template_id)
                if not rule_template:
                    continue

                is_completed = self._check_rule(rule_template, trades_today, daily_note)

                new_status = "completed" if is_completed else "failed"
                await self.instance_repo.update(instance.id, {"status": new_status})


    def _check_rule(self, rule: DisciplineRule, trades: list, daily_note: Note) -> bool:
        # This is a simplified placeholder for the rule evaluation logic
        if rule.name == "Max loss per day":
            total_pnl = sum(trade.p_l for trade in trades if trade.p_l is not None)
            max_loss = float(rule.condition_value.get("amount", 0))
            return total_pnl >= -max_loss

        if rule.name == "Max loss per trade":
            # Handle both fixed amount and percentage
            condition_type = rule.condition_type
            condition_value = rule.condition_value

            max_loss_per_trade = 0
            if condition_type == 'FIXED_AMOUNT':
                max_loss_per_trade = float(condition_value.get("amount", 0))
            elif condition_type == 'PERCENTAGE' and daily_note.starting_balance_of_day:
                percentage = float(condition_value.get("percentage", 0))
                max_loss_per_trade = daily_note.starting_balance_of_day * (percentage / 100.0)

            if max_loss_per_trade <= 0:
                return True # If rule is not configured, it's considered met

            return all(trade.p_l >= -max_loss_per_trade for trade in trades if trade.p_l is not None)

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

    async def bulk_update_rules(self, general_account_id: UUID, trading_account_id: UUID, rules_in: list) -> list[DisciplineRule]:
        # 1. Get existing rule templates from DB
        existing_rules = await self.rule_repo.list_by_general_account(general_account_id)
        existing_rule_map = {str(rule.id): rule for rule in existing_rules}

        incoming_rule_ids = {str(rule.id) for rule in rules_in if rule.id}

        # 2. Delete rules that are not in the incoming list
        for rule_id, rule in existing_rule_map.items():
            if rule_id not in incoming_rule_ids:
                await self.rule_repo.delete(rule.id)

        # 3. Create or update rules
        updated_rules_map = {}
        for rule_data in rules_in:
            rule_dict = rule_data.model_dump()
            rule_id = rule_dict.pop('id', None)

            if rule_id and str(rule_id) in existing_rule_map:
                # Update existing rule
                updated_rule = await self.rule_repo.update(rule_id, rule_dict)
                updated_rules_map[str(updated_rule.id)] = updated_rule
            else:
                # Create new rule
                rule_dict["general_account_id"] = general_account_id
                new_rule = await self.rule_repo.create(rule_dict)
                updated_rules_map[str(new_rule.id)] = new_rule

        # 4. Intelligently update today's checklist
        await self._update_checklist_after_rule_change(general_account_id, trading_account_id, updated_rules_map)

        return list(updated_rules_map.values())

    async def _update_checklist_after_rule_change(self, general_account_id: UUID, trading_account_id: UUID, updated_rules_map: dict):
        today = datetime.date.today()
        daily_note = await self.note_repo.find_by_date_and_folder(today, (await self.folder_repo.find_by_name_and_account("Daily Journal", general_account_id)).id)

        if not daily_note:
            # If no checklist for today, nothing to update. It will be created on next fetch.
            return

        # Get current checklist instances
        current_instances = await self.instance_repo.find_by_journal_and_date(daily_note.id)
        instance_map = {str(inst.rule_template_id): inst for inst in current_instances}

        # Delete instances for rules that no longer exist
        for instance_template_id, instance in instance_map.items():
            if instance_template_id not in updated_rules_map:
                await self.instance_repo.delete(instance.id) # Assumes instance_repo has delete method

        # Add new instances for new rules
        for rule_id, rule in updated_rules_map.items():
            if rule_id not in instance_map and today.weekday() in rule.active_days:
                await self.instance_repo.create_many([{
                    "daily_journal_id": daily_note.id,
                    "rule_template_id": rule.id,
                    "name": rule.name,
                    "rule_type": rule.rule_type,
                    "status": "pending"
                }])

        # Re-evaluate all automated rules after changes
        await self.evaluate_automated_rules(daily_note.id, trading_account_id, today)