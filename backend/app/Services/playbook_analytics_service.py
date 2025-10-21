# app/Services/playbook_analytics_service.py
from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

import asyncio
from app.Repositories.playbook_repository import PlaybookRepository
from app.Repositories.trade_repository import TradeRepository
from app.Schemas.playbook import PlaybookAnalytics, PlaybookAnalyticsMetrics
from app.Schemas.analytics import EquityCurveData
from app.Models.trade import Trade

class PlaybookAnalyticsService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.playbook_repo = PlaybookRepository(db_session)
        self.trade_repo = TradeRepository(db_session)

    async def get_playbook_analytics(self, playbook_id: UUID, current_user_id: UUID, is_admin: bool) -> PlaybookAnalytics:
        """
        Gathers all data required for the playbook detail page analytics using efficient, direct database queries.
        """
        # Esegui le query per statistiche e curva di equità in parallelo
        results = await asyncio.gather(
            self.playbook_repo.get_playbook_with_stats_by_id(playbook_id),
            self.trade_repo.get_equity_curve_data_for_playbook(playbook_id)
        )
        playbook_data = results[0]
        equity_curve_points = results[1]

        if not playbook_data:
            return None  # Sarà gestito come 404 dal controller

        playbook = playbook_data["playbook"]
        stats = playbook_data["stats"]

        # Controllo di sicurezza
        if not is_admin and playbook.general_account.user_id != current_user_id:
            return None  # Sarà gestito come 403 dal controller

        # 1. Calcola le metriche derivate dalle statistiche aggregate
        metrics = self._calculate_metrics_from_stats(stats)

        # 2. Calcola la curva di equità
        equity_curve = self._calculate_equity_curve(equity_curve_points)

        # 3. Assembla la risposta
        return PlaybookAnalytics(
            id=playbook.id,
            title=playbook.title,
            metrics=metrics,
            equity_curve=equity_curve
        )

    def _calculate_metrics_from_stats(self, stats: dict) -> PlaybookAnalyticsMetrics:
        """Calcola e assembla la parte delle metriche della risposta dai dati aggregati."""
        total_trades = stats["total_trades"]
        if total_trades == 0:
            return PlaybookAnalyticsMetrics()  # Restituisce i valori predefiniti

        winning_trades = stats["winning_trades"]
        losing_trades = stats["losing_trades"]
        gross_profit = stats["gross_profit"]
        gross_loss = stats["gross_loss"]

        win_rate = (winning_trades / total_trades) * 100
        avg_winner = gross_profit / winning_trades if winning_trades > 0 else 0
        # La perdita media è un valore positivo
        avg_loser = abs(gross_loss / losing_trades) if losing_trades > 0 else 0
        profit_factor = gross_profit / abs(gross_loss) if gross_loss != 0 else None

        # Calcolo dell'aspettativa
        loss_rate = (losing_trades / total_trades) * 100
        expectancy = ((win_rate / 100) * avg_winner) - ((loss_rate / 100) * avg_loser)

        return PlaybookAnalyticsMetrics(
            net_pnl=stats["total_p_l"],
            trades=total_trades,
            win_rate=win_rate,
            profit_factor=profit_factor,
            missed_trades=0,  # Placeholder
            expectancy=expectancy,
            rules_followed=0.0,  # Placeholder
            average_winner=avg_winner,
            average_loser=avg_loser,
            largest_profit=stats["largest_profit"],
            largest_loss=stats["largest_loss"],
            total_r_multiple=stats["total_r_multiple"]
        )

    def _calculate_equity_curve(self, equity_points: list[tuple[date, float]]) -> EquityCurveData:
        """
        Calcola e assembla la curva di equità dai punti dati (data, pnl) recuperati dal database.
        """
        if not equity_points:
            return EquityCurveData(labels=[], data=[])

        labels = []
        cumulative_pnl_data = []
        cumulative_pnl = 0.0

        for close_time, pnl in equity_points:
            labels.append(close_time.strftime('%Y-%m-%d'))
            cumulative_pnl += pnl
            cumulative_pnl_data.append(round(cumulative_pnl, 2))

        return EquityCurveData(
            labels=labels,
            data=[0.0] + cumulative_pnl_data  # Inizia da 0
        )