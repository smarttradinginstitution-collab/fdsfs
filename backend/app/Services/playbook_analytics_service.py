# app/Services/playbook_analytics_service.py
from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.Repositories.playbook_repository import PlaybookRepository
from app.Services.metrics.metrics_calculator import MetricsCalculator
from app.Schemas.playbook import PlaybookAnalytics, PlaybookAnalyticsMetrics
from app.Schemas.analytics import EquityCurveData
from app.Models.trade import Trade

class PlaybookAnalyticsService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.playbook_repo = PlaybookRepository(db_session)

    async def get_playbook_analytics(self, playbook_id: UUID, current_user_id: UUID, is_admin: bool) -> PlaybookAnalytics:
        """
        Gathers all data required for the playbook detail page analytics.
        """
        playbook = await self.playbook_repo.get_by_id_with_trades(playbook_id)

        if not playbook:
            # This will be caught by the controller and turned into a 404
            return None

        # Basic security check
        if not is_admin and playbook.general_account.user_id != current_user_id:
            # This will be caught and turned into a 403
            return None

        trades = playbook.trades
        # For playbook metrics, initial_balance is not relevant.
        calculator = MetricsCalculator(trades=trades, initial_balance=0.0)

        # 1. Calculate all metrics
        metrics = self._calculate_metrics(calculator, trades)

        # 2. Calculate equity curve
        equity_curve = self._calculate_equity_curve(calculator)

        # 3. Assemble response
        return PlaybookAnalytics(
            id=playbook.id,
            title=playbook.title,
            metrics=metrics,
            equity_curve=equity_curve
        )

    def _calculate_metrics(self, calculator: MetricsCalculator, trades: list[Trade]) -> PlaybookAnalyticsMetrics:
        """Calculates and assembles the metrics part of the response."""
        if not trades:
            return PlaybookAnalyticsMetrics() # Return default values

        win_rate = (calculator.winning_trades_count / calculator.trade_count) * 100 if calculator.trade_count > 0 else 0
        avg_winner = calculator.gross_profit / calculator.winning_trades_count if calculator.winning_trades_count > 0 else 0
        avg_loser = calculator.gross_loss / calculator.losing_trades_count if calculator.losing_trades_count > 0 else 0
        expectancy = calculator._calculate_expectancy(win_rate, avg_winner, avg_loser)
        profit_factor = calculator.gross_profit / calculator.gross_loss if calculator.gross_loss > 0 else None

        # Sum of R-multiples
        total_r_multiple = sum(t.r_multiple for t in trades if t.r_multiple is not None)

        return PlaybookAnalyticsMetrics(
            net_pnl=calculator.net_pnl,
            trades=calculator.trade_count,
            win_rate=win_rate,
            profit_factor=profit_factor,
            missed_trades=0, # Placeholder
            expectancy=expectancy,
            rules_followed=0.0, # Placeholder
            average_winner=avg_winner,
            average_loser=avg_loser,
            largest_profit=max(calculator.pnl_series) if any(p > 0 for p in calculator.pnl_series) else 0,
            largest_loss=min(calculator.pnl_series) if any(p < 0 for p in calculator.pnl_series) else 0,
            total_r_multiple=total_r_multiple
        )

    def _calculate_equity_curve(self, calculator: MetricsCalculator) -> EquityCurveData:
        """Calculates and assembles the equity curve part of the response."""
        # The equity curve from the calculator starts with the initial balance,
        # which is 0 for playbooks. We want to show the cumulative P&L, so we can use it directly.
        # However, the first value is the initial balance (0), and we want to start from the first trade.
        # Also, the labels are dates, which is correct.

        equity_curve_result = calculator.calculate_equity_curve()

        # The calculator's equity curve includes the initial balance as the first point.
        # For our chart, we want to see the progression starting from the first trade's P&L.
        # We also need to format the dates correctly.

        if not calculator.trades:
            return EquityCurveData(labels=[], data=[])

        cumulative_pnl = 0
        data_points = []
        labels = []

        for trade in calculator.trades:
            if trade.p_l is not None:
                cumulative_pnl += trade.p_l
                data_points.append(cumulative_pnl)
                # Use exit timestamp for the label, fallback to entry.
                trade_date = (trade.exit_timestamp or trade.entry_timestamp).strftime('%Y-%m-%d')
                labels.append(trade_date)

        return EquityCurveData(labels=labels, data=data_points)