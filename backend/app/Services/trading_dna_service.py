from __future__ import annotations

from typing import List, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from collections import defaultdict
from itertools import product

from app.Repositories.trade_repository import TradeRepository
from app.Repositories.trading_account_repository import TradingAccountRepository
from app.Repositories.tags_group_repository import TagsGroupRepository
from app.Services.metrics.metrics_calculator import MetricsCalculator
from app.Models.trade import Trade
from app.Models.tag import Tag
from app.Models.mistake import Mistake
from app.Models.psychology_state import PsychologyState
from app.Models.news_impact import NewsImpact


class TradingDnaService:
    """
    Service to perform complex analysis for the Trading DNA report.
    """
    def __init__(self, db: AsyncSession, general_account_id: UUID):
        self.db = db
        self.general_account_id = general_account_id
        self.trade_repo = TradeRepository(self.db)
        self.trading_account_repo = TradingAccountRepository(self.db)
        self.tags_group_repo = TagsGroupRepository(self.db)

    async def generate_report(
        self,
        tag_ids: List[UUID] | None = None,
        mistake_ids: List[UUID] | None = None,
        psychology_state_ids: List[UUID] | None = None,
        news_impact_ids: List[UUID] | None = None,
    ) -> Dict[str, Any]:
        """
        Main method to generate the full Trading DNA report.
        """
        # Fetch trades based on the provided filters. This is the primary dataset for analysis.
        filtered_trades = await self.trade_repo.get_trades_for_dna_analysis(
            general_account_id=self.general_account_id,
            tag_ids=tag_ids,
            mistake_ids=mistake_ids,
            psychology_state_ids=psychology_state_ids,
            news_impact_ids=news_impact_ids,
        )

        golden_combos, toxic_combos = self._discover_and_analyze_combos(filtered_trades)
        group_performance = await self._analyze_group_performance(filtered_trades)

        # For the comparative equity curve, we need all trades to calculate the baseline.
        all_trades = await self.trade_repo.get_trades_for_dna_analysis(self.general_account_id)
        equity_curve = await self._generate_comparative_equity_curve(all_trades, filtered_trades)

        report = {
            "golden_combos": golden_combos,
            "toxic_combos": toxic_combos,
            "group_performance": group_performance,
            "equity_curve": equity_curve,
        }

        return report

    async def _generate_comparative_equity_curve(self, all_trades: List[Trade], filtered_trades: List[Trade]) -> Dict:
        """Generates two equity curves: one for the filtered set and one for the baseline."""
        trading_accounts = await self.trading_account_repo.list_by_general_account_id(self.general_account_id)
        total_initial_balance = sum(acc.initial_balance or 0 for acc in trading_accounts)

        # Calculate equity curve for the filtered trades
        filtered_calculator = MetricsCalculator(filtered_trades, total_initial_balance)
        filtered_curve = filtered_calculator.calculate_equity_curve()

        # Calculate equity curve for the baseline (all other trades)
        filtered_trade_ids = {t.id for t in filtered_trades}
        baseline_trades = [t for t in all_trades if t.id not in filtered_trade_ids]
        baseline_calculator = MetricsCalculator(baseline_trades, total_initial_balance)
        baseline_curve = baseline_calculator.calculate_equity_curve()

        return {
            "filtered_series": filtered_curve,
            "baseline_series": baseline_curve
        }

    async def _analyze_group_performance(self, trades_to_analyze: List[Trade]) -> List[Dict]:
        tag_groups = await self.tags_group_repo.list_tags_groups_by_general_account_id(self.general_account_id)

        performance_data = []
        for group in tag_groups:
            group_tag_ids = {tag.id for tag in group.tags}

            group_trades = [
                trade for trade in trades_to_analyze
                if any(tag.id in group_tag_ids for tag in trade.tags)
            ]

            if not group_trades:
                continue

            metrics = self._calculate_metrics_for_trades(group_trades)
            performance_data.append({
                "group": {"id": str(group.id), "name": group.name},
                "metrics": metrics
            })

        return performance_data

    def _discover_and_analyze_combos(self, trades: List[Trade]) -> Tuple[List[Dict], List[Dict]]:
        golden_combo_trades = defaultdict(list)
        toxic_combo_trades = defaultdict(list)

        for trade in trades:
            if trade.psychology_states:
                if trade.tags:
                    for p_state, tag in product(trade.psychology_states, trade.tags):
                        combo_key = tuple(sorted((('psychology', p_state), ('tag', tag)), key=lambda x: x[0]))
                        golden_combo_trades[combo_key].append(trade)
                if trade.news_impacts:
                    for p_state, news in product(trade.psychology_states, trade.news_impacts):
                        combo_key = tuple(sorted((('psychology', p_state), ('news', news)), key=lambda x: x[0]))
                        golden_combo_trades[combo_key].append(trade)

            if trade.tags and trade.psychology_states and trade.mistakes:
                for tag, p_state, mistake in product(trade.tags, trade.psychology_states, trade.mistakes):
                    combo_key = tuple(sorted((('tag', tag), ('psychology', p_state), ('mistake', mistake)), key=lambda x: x[0]))
                    toxic_combo_trades[combo_key].append(trade)

        analyzed_golden = self._analyze_combos(golden_combo_trades)
        analyzed_toxic = self._analyze_combos(toxic_combo_trades)

        analyzed_golden.sort(key=lambda x: x['metrics']['total_pnl'], reverse=True)
        analyzed_toxic.sort(key=lambda x: x['metrics']['total_pnl'])

        return analyzed_golden[:5], analyzed_toxic[:5]

    def _analyze_combos(self, combo_trades: Dict[Tuple, List[Trade]]) -> List[Dict]:
        analyzed_combos = []
        for combo_key, trades in combo_trades.items():
            if len(trades) < 1: continue # Lowered threshold to 1 to show all combos
            metrics = self._calculate_metrics_for_trades(trades)
            combo_elements = [self._format_label_element(label_type, label_object) for label_type, label_object in combo_key]

            analyzed_combos.append({
                "combo": {"elements": combo_elements},
                "metrics": metrics
            })
        return analyzed_combos

    def _format_label_element(self, label_type: str, label_object: Any) -> Dict:
        item_data = {"id": str(label_object.id), "name": label_object.name, "color": label_object.color}
        if isinstance(label_object, Tag):
            return {"type": "Tag", "group": label_object.group.name if label_object.group else 'N/A', "item": item_data}
        elif isinstance(label_object, Mistake):
            return {"type": "Mistake", "item": item_data}
        elif isinstance(label_object, PsychologyState):
            return {"type": "PsychologyState", "item": item_data}
        elif isinstance(label_object, NewsImpact):
            return {"type": "NewsImpact", "item": item_data}
        return {}

    def _calculate_metrics_for_trades(self, trades: List[Trade]) -> Dict:
        trade_count = len(trades)
        if trade_count == 0:
            return {"trade_count": 0, "win_rate_percent": 0, "average_r_multiple": 0, "total_pnl": 0}

        winning_trades = sum(1 for t in trades if t.p_l > 0)
        total_pnl = sum(t.p_l or 0 for t in trades)
        total_r_multiple = sum(t.r_multiple or 0 for t in trades)

        win_rate_percent = (winning_trades / trade_count) * 100 if trade_count > 0 else 0
        average_r_multiple = total_r_multiple / trade_count if trade_count > 0 else 0

        return {
            "trade_count": trade_count,
            "win_rate_percent": round(win_rate_percent, 2),
            "average_r_multiple": round(average_r_multiple, 2),
            "total_pnl": round(total_pnl, 2)
        }