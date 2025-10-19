from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import date, timedelta
import asyncio
from app.Repositories.trade_repository import TradeRepository
from app.Repositories.daily_rule_instance_repository import DailyRuleInstanceRepository
from app.Repositories.discipline_settings_repository import DisciplineSettingsRepository
from app.Repositories.manual_rule_repository import ManualRuleRepository
from app.Services.discipline_settings_service import DisciplineSettingsService
from app.Schemas.discipline_settings_schema import DisciplineSettingsSchema

class RuleStatisticsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.trade_repo = TradeRepository(db)
        self.instance_repo = DailyRuleInstanceRepository(db)
        self.settings_repo = DisciplineSettingsRepository(db)
        self.manual_rule_repo = ManualRuleRepository(db)
        self.discipline_service = DisciplineSettingsService(db)

    async def get_rules_with_statistics(self, general_account_id: UUID, trading_account_id: UUID):
        settings = await self.settings_repo.get_by_general_account_id(general_account_id)
        manual_rules = await self.manual_rule_repo.list_by_general_account(general_account_id)

        if not settings:
            return []

        today = date.today()
        date_range = [today - timedelta(days=i) for i in range(30)]

        all_rules_with_stats = []

        automated_rules = self._get_automated_rules_from_settings(settings)

        for rule in automated_rules:
            stats = await self._calculate_automated_rule_stats(rule, general_account_id, trading_account_id, date_range)
            all_rules_with_stats.append({**rule, **stats})

        for rule in manual_rules:
            stats = await self._calculate_manual_rule_stats(rule.id, trading_account_id, date_range)
            all_rules_with_stats.append({
                "id": rule.id,
                "name": rule.name,
                "isManual": True,
                **stats
            })

        return all_rules_with_stats

    def _get_automated_rules_from_settings(self, settings):
        rules = []
        # Convert the ORM model to a Pydantic schema to ensure it's serializable
        settings_schema = DisciplineSettingsSchema.model_validate(settings)

        if settings.start_day_by: rules.append({"id": "auto_start_day", "name": "Start my day by", "settings": settings_schema, "isManual": False})
        if settings.link_trades_to_playbook_threshold is not None: rules.append({"id": "auto_link_playbook", "name": "Link trades to playbook", "settings": settings_schema, "isManual": False})
        if settings.trade_has_stop_loss_threshold is not None: rules.append({"id": "auto_stop_loss", "name": "Trade has stop loss", "settings": settings_schema, "isManual": False})
        if settings.max_loss_per_trade_value is not None: rules.append({"id": "auto_max_loss_trade", "name": "Max loss per trade", "settings": settings_schema, "isManual": False})
        if settings.max_loss_per_day is not None: rules.append({"id": "auto_max_loss_day", "name": "Max loss per day", "settings": settings_schema, "isManual": False})
        return rules

    async def _calculate_automated_rule_stats(self, rule, general_account_id, trading_account_id, date_range):
        total_days = 0
        completed_days = 0
        performance_values = []

        for day in date_range:
            daily_statuses = await self.discipline_service.evaluate_automated_rules(rule['settings'], general_account_id, trading_account_id, day)
            rule_status_for_day = next((s for s in daily_statuses if s['name'] == rule['name']), None)

            if rule_status_for_day:
                total_days += 1
                if rule_status_for_day['status'] == 'completed':
                    completed_days += 1

                # Performance calculation
                if rule['name'] == 'Link trades to playbook':
                    total_trades = await self.trade_repo.get_trades_count(trading_account_id, day)
                    if total_trades > 0:
                        linked_trades = await self.trade_repo.get_trades_linked_to_playbook_count(trading_account_id, day)
                        performance_values.append((linked_trades / total_trades) * 100)
                elif rule['name'] == 'Trade has stop loss':
                    total_trades = await self.trade_repo.get_trades_count(trading_account_id, day)
                    if total_trades > 0:
                        trades_with_sl = await self.trade_repo.get_trades_with_stop_loss_count(trading_account_id, day)
                        performance_values.append((trades_with_sl / total_trades) * 100)
                elif rule['name'] == 'Max loss per day':
                    pnl = await self.trade_repo.get_daily_pnl(trading_account_id, day)
                    if pnl is not None:
                        performance_values.append(float(pnl))

        follow_rate = (completed_days / total_days) * 100 if total_days > 0 else 100.0

        avg_performance = "N/A"
        if performance_values:
            avg_performance = sum(performance_values) / len(performance_values)

        return {"follow_rate": follow_rate, "avg_performance": avg_performance}

    async def _calculate_manual_rule_stats(self, rule_id, trading_account_id, date_range):
        instances = await self.instance_repo.find_by_rule_and_date_range(rule_id, trading_account_id, date_range)
        total_days = len(instances)
        if total_days == 0:
            return {"follow_rate": 100.0, "avg_performance": "-"}

        completed_days = sum(1 for i in instances if i.status == 'completed')
        follow_rate = (completed_days / total_days) * 100
        return {"follow_rate": follow_rate, "avg_performance": "-"}