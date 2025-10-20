import datetime
import asyncio
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.Repositories.discipline_settings_repository import DisciplineSettingsRepository
from app.Repositories.manual_rule_repository import ManualRuleRepository
from app.Repositories.daily_rule_instance_repository import DailyRuleInstanceRepository
from app.Repositories.trade_repository import TradeRepository
from app.Repositories.note_repository import NoteRepository
from app.Repositories.notebook_folder_repository import NotebookFolderRepository
from app.Schemas.discipline_settings_schema import DisciplineSettingsUpdate
from app.Schemas.notebook import NoteCreate
from app.Schemas.daily_rule_instance_schema import DailyRuleInstanceSchema

class DisciplineSettingsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings_repo = DisciplineSettingsRepository(db)
        self.manual_rule_repo = ManualRuleRepository(db)
        self.instance_repo = DailyRuleInstanceRepository(db)
        self.trade_repo = TradeRepository(db)
        self.note_repo = NoteRepository(db)
        self.folder_repo = NotebookFolderRepository(db)

    async def get_settings_by_general_account(self, general_account_id: UUID):
        return await self.settings_repo.get_by_general_account_id(general_account_id)

    async def create_or_update_settings(self, general_account_id: UUID, settings_data: DisciplineSettingsUpdate):
        settings_dict = settings_data.model_dump(exclude_unset=True)

        existing_settings = await self.settings_repo.get_by_general_account_id(general_account_id)

        if existing_settings:
            return await self.settings_repo.update(existing_settings.id, settings_dict)
        else:
            settings_dict['general_account_id'] = general_account_id
            return await self.settings_repo.create(settings_dict)

    async def get_or_create_daily_checklist(self, general_account_id: UUID, trading_account_id: UUID):
        today = datetime.date.today()
        settings = await self.get_settings_by_general_account(general_account_id)

        if not settings or today.weekday() + 1 not in settings.trading_days:
            return {"automated_rules": [], "manual_rules": []}

        daily_note = await self._get_or_create_daily_note(general_account_id, today)

        await self._create_manual_rule_instances_for_day(daily_note.id, general_account_id, trading_account_id, today)

        automated_rules_status = await self.evaluate_automated_rules(settings, general_account_id, trading_account_id, today)
        manual_rules_instances = await self.instance_repo.find_by_note_and_trading_account(daily_note.id, trading_account_id)

        manual_rules_schemas = [DailyRuleInstanceSchema.model_validate(instance) for instance in manual_rules_instances]

        return {
            "automated_rules": automated_rules_status,
            "manual_rules": manual_rules_schemas
        }

    async def _get_or_create_daily_note(self, general_account_id: UUID, date: datetime.date):
        daily_journal_folder = await self.folder_repo.find_by_name_and_account("Daily Journal", general_account_id)
        if not daily_journal_folder:
            from app.Schemas.notebook import NotebookFolderCreate
            folder_create_schema = NotebookFolderCreate(name="Daily Journal", folder_type='default')
            daily_journal_folder = await self.folder_repo.create(folder_create_schema, general_account_id)

        daily_note = await self.note_repo.find_by_date_and_folder(date, daily_journal_folder.id)
        if not daily_note:
            note_schema = NoteCreate(
                folder_id=daily_journal_folder.id,
                title=f"Journal for {date.strftime('%Y-%m-%d')}",
                note_date=date,
                content={"blocks": []}
            )
            daily_note = await self.note_repo.create(note_schema)
        return daily_note

    async def _create_manual_rule_instances_for_day(self, daily_note_id: UUID, general_account_id: UUID, trading_account_id: UUID, date: datetime.date):
        manual_rules = await self.manual_rule_repo.list_by_general_account(general_account_id)

        for rule in manual_rules:
            if date.weekday() + 1 in rule.frequency:
                await self.instance_repo.get_or_create(
                    manual_rule_id=rule.id,
                    daily_journal_id=daily_note_id,
                    trading_account_id=trading_account_id,
                    date=date
                )

    async def evaluate_automated_rules(self, settings, general_account_id: UUID, trading_account_id: UUID, date: datetime.date):
        results_by_day = await self.evaluate_automated_rules_for_date_range(
            settings, general_account_id, trading_account_id, date, date
        )
        return results_by_day.get(date, [])

    async def evaluate_automated_rules_for_date_range(
        self, settings, general_account_id: UUID, trading_account_id: UUID, start_date: datetime.date, end_date: datetime.date
    ):
        trade_stats_by_day, daily_pnl_by_day, daily_notes_by_day = await asyncio.gather(
            self.trade_repo.get_trade_stats_by_day_for_date_range(trading_account_id, start_date, end_date),
            self.trade_repo.get_daily_pnl_for_date_range(trading_account_id, start_date, end_date),
            self.note_repo.find_by_date_range_and_general_account(start_date, end_date, general_account_id)
        )

        # For "Max loss per trade", we still need individual trades and current account balance
        trades_in_range = await self.trade_repo.get_filtered_trades(trading_account_id, start_date, end_date)
        account_balance = await self.trade_repo.get_account_balance(trading_account_id)

        trades_by_day = {}
        for trade in trades_in_range:
            day = trade.entry_timestamp.date()
            if day not in trades_by_day:
                trades_by_day[day] = []
            trades_by_day[day].append(trade)

        results = {}
        current_date = start_date
        while current_date <= end_date:
            stats_today = trade_stats_by_day.get(current_date, {"total_trades": 0, "trades_with_sl": 0, "trades_linked_to_playbook": 0})
            pnl_today = daily_pnl_by_day.get(current_date, 0.0)
            note_today = daily_notes_by_day.get(current_date)
            trades_today = trades_by_day.get(current_date, [])

            rules_status = []

            # Rule: Start my day by
            if settings.start_day_by:
                status = "completed" if note_today and note_today.created_at.time() <= settings.start_day_by else "failed"
                rules_status.append({"name": "Start my day by", "status": status, "progress": None})

            # Rule: Link trades to playbook
            if settings.link_trades_to_playbook_threshold is not None:
                total, completed = stats_today["total_trades"], stats_today["trades_linked_to_playbook"]
                status = "pending"
                if total > 0:
                    percentage = (completed / total) * 100
                    status = "completed" if percentage >= settings.link_trades_to_playbook_threshold else "failed"
                rules_status.append({"name": "Link trades to playbook", "status": status, "progress": f"{completed}/{total}"})

            # Rule: Trade has stop loss
            if settings.trade_has_stop_loss_threshold is not None:
                total, completed = stats_today["total_trades"], stats_today["trades_with_sl"]
                status = "pending"
                if total > 0:
                    percentage = (completed / total) * 100
                    status = "completed" if percentage >= settings.trade_has_stop_loss_threshold else "failed"
                rules_status.append({"name": "Trade has stop loss", "status": status, "progress": f"{completed}/{total}"})

            # Rule: Max loss per trade
            if settings.max_loss_per_trade_value is not None:
                status = "pending"
                violations = 0
                if trades_today:
                    status = "completed"
                    for trade in trades_today:
                        if trade.p_l is None: continue
                        max_loss = settings.max_loss_per_trade_value
                        if settings.max_loss_per_trade_type == '%':
                            max_loss = (account_balance / 100) * settings.max_loss_per_trade_value
                        if trade.p_l < -max_loss:
                            status = "failed"
                            violations += 1
                progress = f"{violations}/{len(trades_today)}" if trades_today else "0/0"
                rules_status.append({"name": "Max loss per trade", "status": status, "progress": progress})

            # Rule: Max loss per day
            if settings.max_loss_per_day is not None:
                status = "completed" if pnl_today >= -settings.max_loss_per_day else "failed"
                progress = f"${pnl_today:.2f}/$-{settings.max_loss_per_day:.2f}"
                rules_status.append({"name": "Max loss per day", "status": status, "progress": progress})

            results[current_date] = rules_status
            current_date += datetime.timedelta(days=1)

        return results

    async def update_manual_rule_status(self, instance_id: UUID, status: str):
        instance = await self.instance_repo.get_by_id(instance_id)
        if instance:
            return await self.instance_repo.update(instance_id, {"status": status})
        return None
