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
        settings, manual_rules = await asyncio.gather(
            self.settings_repo.get_by_general_account_id(general_account_id),
            self.manual_rule_repo.list_by_general_account(general_account_id)
        )

        if not settings:
            return []

        today = date.today()
        start_date = today - timedelta(days=29)

        # Fetch manual rule stats and evaluated automated rule statuses in parallel
        manual_rule_stats, statuses_by_day = await asyncio.gather(
            self.instance_repo.get_stats_by_manual_rule_for_date_range(
                [rule.id for rule in manual_rules], trading_account_id, start_date, today
            ),
            self.discipline_service.evaluate_automated_rules_for_date_range(
                settings, general_account_id, trading_account_id, start_date, today
            )
        )

        all_rules_with_stats = []
        automated_rules = self._get_automated_rules_from_settings(settings)

        for rule in automated_rules:
            stats = self._calculate_automated_rule_stats(rule, statuses_by_day)
            all_rules_with_stats.append({**rule, **stats})

        for rule in manual_rules:
            stats = manual_rule_stats.get(rule.id, {"follow_rate": 100.0})
            all_rules_with_stats.append({
                "id": rule.id,
                "name": rule.name,
                "isManual": True,
                "follow_rate": stats["follow_rate"],
                "avg_performance": "-"
            })

        return all_rules_with_stats

    def _get_automated_rules_from_settings(self, settings):
        rules = []
        settings_schema = DisciplineSettingsSchema.model_validate(settings)
        if settings.start_day_by: rules.append({"id": "auto_start_day", "name": "Start my day by", "settings": settings_schema, "isManual": False})
        if settings.link_trades_to_playbook_threshold is not None: rules.append({"id": "auto_link_playbook", "name": "Link trades to playbook", "settings": settings_schema, "isManual": False})
        if settings.trade_has_stop_loss_threshold is not None: rules.append({"id": "auto_stop_loss", "name": "Trade has stop loss", "settings": settings_schema, "isManual": False})
        if settings.max_loss_per_trade_value is not None: rules.append({"id": "auto_max_loss_trade", "name": "Max loss per trade", "settings": settings_schema, "isManual": False})
        if settings.max_loss_per_day is not None: rules.append({"id": "auto_max_loss_day", "name": "Max loss per day", "settings": settings_schema, "isManual": False})
        return rules

    def _calculate_automated_rule_stats(self, rule, statuses_by_day):
        total_days = 0
        completed_days = 0
        performance_values = []

        for day, daily_statuses in statuses_by_day.items():
            rule_status_for_day = next((s for s in daily_statuses if s['name'] == rule['name']), None)

            if rule_status_for_day:
                total_days += 1
                if rule_status_for_day['status'] == 'completed':
                    completed_days += 1

                # Extract performance data from progress string
                progress = rule_status_for_day.get("progress")
                if progress:
                    if rule['name'] in ['Link trades to playbook', 'Trade has stop loss']:
                        parts = progress.split('/')
                        if len(parts) == 2 and int(parts[1]) > 0:
                            performance_values.append((int(parts[0]) / int(parts[1])) * 100)
                    elif rule['name'] == 'Max loss per day':
                        # Example progress: "$123.45/$-500.00"
                        pnl_str = progress.split('/')[0].replace('$', '')
                        try:
                            performance_values.append(float(pnl_str))
                        except (ValueError, IndexError):
                            pass

        follow_rate = (completed_days / total_days) * 100 if total_days > 0 else 100.0
        avg_performance = sum(performance_values) / len(performance_values) if performance_values else "N/A"

        return {"follow_rate": follow_rate, "avg_performance": avg_performance}
