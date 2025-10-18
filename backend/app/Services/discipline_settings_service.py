import datetime
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

        # If no settings or not a trading day, return empty checklist
        if not settings or today.weekday() + 1 not in settings.trading_days:
            return {"automated_rules": [], "manual_rules": []}

        # Logic to get or create the daily note (simplified)
        daily_note = await self._get_or_create_daily_note(general_account_id, today)

        # Create instances for manual rules for the day if they don't exist
        await self._create_manual_rule_instances_for_day(daily_note.id, general_account_id, trading_account_id, today)

        # Evaluate automated rules and get their status
        automated_rules_status = await self.evaluate_automated_rules(settings, trading_account_id, today)

        # Get manual rule instances for the day
        manual_rules_instances = await self.instance_repo.find_by_note_and_trading_account(daily_note.id, trading_account_id)

        return {
            "automated_rules": automated_rules_status,
            "manual_rules": manual_rules_instances
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
                # This check should be done in the repository to avoid race conditions
                await self.instance_repo.get_or_create(
                    manual_rule_id=rule.id,
                    daily_journal_id=daily_note_id,
                    trading_account_id=trading_account_id,
                    date=date
                )

    async def evaluate_automated_rules(self, settings, trading_account_id: UUID, date: datetime.date):
        trades_today = await self.trade_repo.get_filtered_trades(trading_account_id, date, date)
        # This is where the logic for each automated rule goes
        # For now, returning a placeholder
        return []

    async def update_manual_rule_status(self, instance_id: UUID, status: str):
        # This logic remains largely the same
        instance = await self.instance_repo.get_by_id(instance_id)
        if instance:
            return await self.instance_repo.update(instance_id, {"status": status})
        return None