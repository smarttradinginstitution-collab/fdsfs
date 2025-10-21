# app/Services/playbook_analytics_service.py
from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from datetime import datetime
from decimal import Decimal
from app.Repositories.playbook_repository import PlaybookRepository
from app.Schemas.playbook import PlaybookAnalytics, PlaybookAnalyticsMetrics
from app.Schemas.analytics import EquityCurveData

class PlaybookAnalyticsService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.playbook_repo = PlaybookRepository(db_session)

    async def get_playbook_analytics(self, playbook_id: UUID, current_user_id: UUID, is_admin: bool) -> PlaybookAnalytics:
        """
        Gathers all data required for the playbook detail page analytics using
        a single, optimized database query.
        """
        # Step 1: Verify ownership (without loading all trades)
        playbook = await self.playbook_repo.get_by_id(playbook_id)
        if not playbook:
            return None
        if not is_admin and playbook.general_account.user_id != current_user_id:
            return None

        # Step 2: Fetch pre-aggregated stats from the repository
        stats = await self.playbook_repo.get_analytics_by_playbook_id(playbook_id)
        if not stats:
            # Handle case with no trades
            return PlaybookAnalytics(
                id=playbook.id,
                title=playbook.title,
                metrics=PlaybookAnalyticsMetrics(),
                equity_curve=EquityCurveData(labels=[], data=[0.0])
            )

        # Step 3: Calculate derived metrics
        metrics = self._calculate_derived_metrics(stats)

        # Step 4: Format equity curve data
        equity_curve = self._format_equity_curve(stats['equity_curve_data'])

        # Step 5: Assemble response
        return PlaybookAnalytics(
            id=playbook.id,
            title=playbook.title,
            metrics=metrics,
            equity_curve=equity_curve
        )

    def _calculate_derived_metrics(self, stats: dict) -> PlaybookAnalyticsMetrics:
        """Calculates derived metrics from the raw aggregated data, handling None values."""

        # Securely retrieve raw stats, defaulting None to 0 or 0.0
        net_pnl = stats.get('net_pnl') or 0.0
        trades_count = stats.get('trades_count') or 0
        winning_trades = stats.get('winning_trades') or 0
        losing_trades = stats.get('losing_trades') or 0
        gross_profit = stats.get('gross_profit') or 0.0
        gross_loss = abs(stats.get('gross_loss') or 0.0)
        largest_profit = stats.get('largest_profit') or 0.0
        largest_loss = stats.get('largest_loss') or 0.0
        total_r_multiple = stats.get('total_r_multiple') or 0.0

        # Use Decimal for precise financial calculations
        gross_profit_dec = Decimal(str(gross_profit))
        gross_loss_dec = Decimal(str(gross_loss))

        # Calculate derived metrics
        win_rate = (winning_trades / trades_count) * 100 if trades_count > 0 else 0
        loss_rate = (losing_trades / trades_count) * 100 if trades_count > 0 else 0
        profit_factor = float(gross_profit_dec / gross_loss_dec) if gross_loss_dec > 0 else None
        avg_winner = float(gross_profit_dec / winning_trades) if winning_trades > 0 else 0
        avg_loser = float(gross_loss_dec / losing_trades) if losing_trades > 0 else 0
        expectancy = ((win_rate / 100) * avg_winner) - ((loss_rate / 100) * avg_loser)

        return PlaybookAnalyticsMetrics(
            net_pnl=float(net_pnl),
            trades=trades_count,
            win_rate=win_rate,
            profit_factor=profit_factor,
            expectancy=expectancy,
            average_winner=avg_winner,
            average_loser=avg_loser,
            largest_profit=float(largest_profit),
            largest_loss=float(largest_loss),
            total_r_multiple=float(total_r_multiple),
            missed_trades=0,  # Placeholder
            rules_followed=0.0,  # Placeholder
        )

    def _format_equity_curve(self, curve_data: list) -> EquityCurveData:
        """Formats the equity curve data from the database into the Pydantic schema."""
        if not curve_data:
            return EquityCurveData(labels=[], data=[0.0])

        # Sort data by date, just in case
        sorted_curve = sorted(curve_data, key=lambda x: x['date'])

        labels = [datetime.fromisoformat(item['date']).date() for item in sorted_curve]
        # Start the curve with an initial balance of 0
        data = [0.0] + [float(item['cumulative_pnl']) for item in sorted_curve]

        return EquityCurveData(labels=labels, data=data)