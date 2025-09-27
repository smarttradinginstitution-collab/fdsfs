# app/Services/metrics/metrics_calculator.py

from decimal import Decimal
import numpy as np
from dateutil.parser import parse
from scipy.stats import skew, kurtosis
from datetime import datetime
import pytz

class MetricsCalculator:
    def __init__(self, trades, user_timezone: str = "UTC"):
        self.all_trades = trades
        self.user_timezone = user_timezone
        try:
            self.tz = pytz.timezone(self.user_timezone)
        except pytz.UnknownTimeZoneError:
            self.tz = pytz.utc

        if self.all_trades:
            self._prepare_trades()

    def _convert_to_local_tz(self, dt_obj: datetime | str | None) -> datetime | None:
        """
        Converte un oggetto datetime (o una stringa parsabile) al fuso orario
        dell'utente. Se il datetime è naive, lo considera UTC.
        """
        if dt_obj is None:
            return None
        if isinstance(dt_obj, str):
            dt_obj = parse(dt_obj)

        if dt_obj.tzinfo:
            return dt_obj.astimezone(self.tz)
        else:
            return pytz.utc.localize(dt_obj).astimezone(self.tz)

    @staticmethod
    def filter_trades(trades, filters):
        """
        Filtra una lista di trade (oggetti o dizionari) in base a criteri calcolati.
        """
        if not filters:
            return trades

        def get_attr(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        filtered_trades = []
        for trade in trades:
            # Duration filter
            min_dur, max_dur = filters.get('min_duration'), filters.get('max_duration')
            entry_ts = get_attr(trade, 'entry_timestamp')
            exit_ts = get_attr(trade, 'exit_timestamp')
            if (min_dur is not None or max_dur is not None) and entry_ts and exit_ts:
                duration_minutes = (exit_ts - entry_ts).total_seconds() / 60
                if (min_dur is not None and duration_minutes < min_dur) or \
                   (max_dur is not None and duration_minutes > max_dur):
                    continue

            # R-Multiple filter
            min_rr, max_rr = filters.get('min_rr'), filters.get('max_rr')
            r_multiple = get_attr(trade, 'r_multiple')
            if r_multiple is not None and (min_rr is not None or max_rr is not None):
                if (min_rr is not None and r_multiple < min_rr) or \
                   (max_rr is not None and r_multiple > max_rr):
                    continue

            filtered_trades.append(trade)

        return filtered_trades

    def _prepare_trades(self):
        """
        Pre-calcola P&L netto, MAE/MFE, ROI e converte le date per ogni trade.
        Aggiunge questi valori come attributi dinamici all'oggetto trade.
        """
        for trade in self.all_trades:
            # 1. Calcolo P&L Netto
            gross_pnl = Decimal(trade.gross_p_l) if trade.gross_p_l is not None else Decimal('0')
            fees = Decimal(trade.fees) if trade.fees is not None else Decimal('0')
            commissions = Decimal(trade.commissions) if trade.commissions is not None else Decimal('0')
            trade.net_pnl = gross_pnl - fees - commissions

            # 2. Calcolo MAE/MFE
            entry = Decimal(trade.entry_price) if trade.entry_price is not None else Decimal(0)
            lowest = Decimal(trade.lowest_price_during_trade) if trade.lowest_price_during_trade is not None else Decimal(0)
            highest = Decimal(trade.highest_price_during_trade) if trade.highest_price_during_trade is not None else Decimal(0)
            direction = trade.direction
            
            if entry > 0 and lowest > 0 and highest > 0 and direction:
                if direction == 'Long':
                    trade.mae_points = float(entry - lowest)
                    trade.mfe_points = float(highest - entry)
                elif direction == 'Short':
                    trade.mae_points = float(highest - entry)
                    trade.mfe_points = float(entry - lowest)
            else:
                trade.mae_points, trade.mfe_points = 0, 0

            # 3. Net ROI
            entry_price = Decimal(trade.entry_price) if trade.entry_price is not None else Decimal('0')
            position_size = Decimal(trade.position_size) if trade.position_size is not None else Decimal('0')
            cost = entry_price * position_size
            trade.net_roi = float((trade.net_pnl / cost) * 100) if cost != 0 else 0.0

            # 4. Conversione e localizzazione delle date (sovrascrive l'originale)
            trade.created_at = self._convert_to_local_tz(trade.created_at)
            trade.entry_timestamp = self._convert_to_local_tz(trade.entry_timestamp)
            trade.exit_timestamp = self._convert_to_local_tz(trade.exit_timestamp)

    def _get_empty_response(self):
        """Struttura di default quando non ci sono trade."""
        stats_keys = [
            'total_pl', 'trade_count', 'avg_win', 'avg_loss', 'profit_factor', 'expectancy',
            'avg_sell_efficiency', 'avg_total_efficiency', 'avg_planned_rr', 'avg_realized_rr',
            'max_drawdown_abs', 'max_drawdown_pct', 'sharpe_ratio', 'sortino_ratio',
            'calmar_ratio', 'skewness', 'kurtosis', 'var_95', 'cvar_95'
        ]
        return {
            'trades': [],
            'stats': {key: 0 for key in stats_keys},
            'equity_curve_data': [], 'setup_chart_data': [],
            'r_multiple_data': {'labels': [], 'data': []}
        }

    def _calculate_base_stats(self):
        """Statistiche di base (P&L, win/loss, etc.) basate su net_pnl."""
        pnl_data = [t.net_pnl for t in self.all_trades]
        winning_trades_pnl = [pnl for pnl in pnl_data if pnl > 0]
        losing_trades_pnl = [pnl for pnl in pnl_data if pnl < 0]
        breakeven_trades_count = len([pnl for pnl in pnl_data if pnl == 0])
        winning_trades = [t for t in self.all_trades if hasattr(t, 'net_pnl') and t.net_pnl > 0]

        long_wins = long_losses = long_be = 0
        short_wins = short_losses = short_be = 0
        for trade in self.all_trades:
            pnl = trade.net_pnl
            if trade.direction == 'Long':
                if pnl > 0: long_wins += 1
                elif pnl < 0: long_losses += 1
                else: long_be += 1
            elif trade.direction == 'Short':
                if pnl > 0: short_wins += 1
                elif pnl < 0: short_losses += 1
                else: short_be += 1

        long_trades_count = long_wins + long_losses + long_be
        short_trades_count = short_wins + short_losses + short_be
        longs_win_percentage = (Decimal(long_wins) / long_trades_count * 100) if long_trades_count > 0 else Decimal(0)
        shorts_win_percentage = (Decimal(short_wins) / short_trades_count * 100) if short_trades_count > 0 else Decimal(0)

        trade_count = len(self.all_trades)
        win_count, loss_count = len(winning_trades_pnl), len(losing_trades_pnl)

        total_pl = sum(pnl_data)
        total_win = sum(winning_trades_pnl)
        total_loss = abs(sum(losing_trades_pnl))

        avg_win = total_win / win_count if win_count > 0 else Decimal(0)
        avg_loss = total_loss / loss_count if loss_count > 0 else Decimal(0)
        avg_trade_pnl = total_pl / trade_count if trade_count > 0 else Decimal(0)
        avg_win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else Decimal('inf')

        profit_factor_val = Decimal(0)
        profit_factor_label = "0.00"
        if total_loss > 0:
            pf_decimal = total_win / total_loss
            profit_factor_val = pf_decimal
            profit_factor_label = f"{pf_decimal:.2f}"
        elif total_win > 0:
            profit_factor_val = Decimal('inf')
            profit_factor_label = "∞"

        win_rate = Decimal(win_count) / trade_count if trade_count > 0 else Decimal(0)
        expectancy = (win_rate * avg_win) - ((1-win_rate) * avg_loss)

        largest_profit = max(winning_trades_pnl) if winning_trades_pnl else Decimal(0)
        largest_loss = min(losing_trades_pnl) if losing_trades_pnl else Decimal(0)

        return {
            'total_pl': total_pl,
            'trade_count': trade_count,
            'winning_trades_count': win_count,
            'losing_trades_count': loss_count,
            'breakeven_trades_count': breakeven_trades_count,
            'winning_trades': winning_trades,
            'avg_win': avg_win, 'avg_loss': avg_loss,
            'profit_factor': profit_factor_val,
            'profit_factor_label': profit_factor_label,
            'expectancy': expectancy,
            'win_rate': win_rate * 100,
            'average_trade_pnl': avg_trade_pnl,
            'average_win_loss_ratio': avg_win_loss_ratio,
            'largest_profit': largest_profit,
            'largest_loss': largest_loss,
            'longs_win_percentage': longs_win_percentage,
            'shorts_win_percentage': shorts_win_percentage,
            'long_trades_analysis': {'wins': long_wins, 'losses': long_losses, 'breakeven': long_be, 'total': long_trades_count},
            'short_trades_analysis': {'wins': short_wins, 'losses': short_losses, 'breakeven': short_be, 'total': short_trades_count},
            'losing_trades_pnl': losing_trades_pnl,
            'pnl_data': pnl_data
        }

    def _calculate_advanced_stats(self, base_stats):
        """Statistiche avanzate (efficienza, R:R, drawdown, ecc.)."""
        sell_efficiencies, total_efficiencies, planned_rrs, realized_rrs = [], [], [], []
        for t in base_stats['winning_trades']:
            entry_price = Decimal(t.entry_price) if t.entry_price is not None else None
            exit_price = Decimal(t.exit_price) if t.exit_price is not None else None
            mfe_points = Decimal(t.mfe_points) if hasattr(t, 'mfe_points') and t.mfe_points is not None else None

            if mfe_points and mfe_points > 0 and entry_price is not None and exit_price is not None:
                pnl_in_points = abs(exit_price - entry_price)
                pnl_in_points = min(pnl_in_points, mfe_points)
                if mfe_points > 0:
                    sell_efficiencies.append(pnl_in_points / mfe_points)

        for t in self.all_trades:
            if hasattr(t, 'mfe_points') and hasattr(t, 'mae_points') and t.mfe_points is not None and t.mae_points is not None:
                mfe_points, mae_points = Decimal(t.mfe_points), Decimal(t.mae_points)
                if (mfe_points + mae_points) > 0:
                    total_efficiencies.append(mfe_points / (mfe_points + mae_points))

            entry = Decimal(t.entry_price) if t.entry_price is not None else Decimal('0')
            sl = Decimal(t.stop_loss_price) if t.stop_loss_price is not None else Decimal('0')
            tp = Decimal(t.take_profit_price) if t.take_profit_price is not None else Decimal('0')
            potential_risk_points = abs(entry - sl) if entry and sl else Decimal(0)

            if potential_risk_points > 0:
                potential_reward_points = abs(tp - entry) if tp and entry else Decimal(0)
                planned_rrs.append(potential_reward_points / potential_risk_points)

            if t.r_multiple is not None:
                realized_rrs.append(Decimal(t.r_multiple))

        fallback_date = self._convert_to_local_tz(datetime(1970, 1, 1))
        self.all_trades.sort(key=lambda x: x.entry_timestamp or fallback_date)
        safe_pnl_floats = [float(pnl) for pnl in base_stats['pnl_data']]
        equity_curve_data = [{'date': (t.entry_timestamp or fallback_date).strftime('%d/%m/%Y'), 'pl': pnl} for t, pnl in zip(self.all_trades, np.cumsum(safe_pnl_floats))]

        equity_points = [0] + [p['pl'] for p in equity_curve_data]
        peak_array = np.maximum.accumulate(equity_points)
        drawdown = peak_array - equity_points
        max_drawdown_abs = Decimal(np.max(drawdown)) if drawdown.size > 0 else Decimal(0)

        recovery_factor = base_stats['total_pl'] / max_drawdown_abs if max_drawdown_abs > 0 else Decimal('inf')
        all_drawdowns, in_drawdown = [], False
        current_dd_peak = equity_points[0]
        for point in equity_points[1:]:
            if point >= current_dd_peak:
                current_dd_peak = point
                in_drawdown = False
            else:
                if not in_drawdown:
                    in_drawdown = True
                    all_drawdowns.append([])
                all_drawdowns[-1].append(current_dd_peak - point)
        max_dd_values = [max(dd) for dd in all_drawdowns if dd]
        average_drawdown = np.mean(max_dd_values) if max_dd_values else Decimal(0)

        hold_times_minutes = []
        pnl_by_day_of_week = {i: Decimal(0) for i in range(7)}
        pnl_by_hour = {i: Decimal(0) for i in range(24)}
        for trade in self.all_trades:
            entry, exit_ts = trade.entry_timestamp, trade.exit_timestamp
            if entry and exit_ts:
                hold_times_minutes.append((exit_ts - entry).total_seconds() / 60)
            if entry:
                pnl_by_day_of_week[entry.weekday()] += trade.net_pnl
                pnl_by_hour[entry.hour] += trade.net_pnl

        average_hold_time = np.mean(hold_times_minutes) if hold_times_minutes else 0
        longest_trade_duration = max(hold_times_minutes) if hold_times_minutes else 0
        day_names = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
        performance_by_day_of_week = {day_names[i]: pnl for i, pnl in pnl_by_day_of_week.items()}
        performance_by_hour = {f"{h:02d}:00": pnl for h, pnl in pnl_by_hour.items()}

        daily_pnl, daily_volume = {}, {}
        for trade in self.all_trades:
            if trade.entry_timestamp:
                trade_date = trade.entry_timestamp.date()
                daily_pnl.setdefault(trade_date, Decimal(0))
                daily_volume.setdefault(trade_date, Decimal(0))
                volume = Decimal(trade.position_size) if trade.position_size is not None else Decimal('0')
                daily_pnl[trade_date] += trade.net_pnl
                daily_volume[trade_date] += volume

        daily_pnl_values = list(daily_pnl.values())
        winning_days_pnl = [p for p in daily_pnl_values if p > 0]
        losing_days_pnl = [p for p in daily_pnl_values if p < 0]

        average_daily_pnl = np.mean([float(v) for v in daily_pnl_values]) if daily_pnl_values else Decimal(0)
        average_winning_day_pnl = np.mean([float(v) for v in winning_days_pnl]) if winning_days_pnl else Decimal(0)
        average_losing_day_pnl = np.mean([float(v) for v in losing_days_pnl]) if losing_days_pnl else Decimal(0)
        largest_profitable_day = max(winning_days_pnl) if winning_days_pnl else Decimal(0)
        largest_losing_day = min(losing_days_pnl) if losing_days_pnl else Decimal(0)
        net_daily_pnl_chart = [{'date': d.strftime('%Y-%m-%d'), 'pnl': float(p)} for d, p in daily_pnl.items()]

        total_trading_days = len(daily_pnl_values)
        winning_days = len(winning_days_pnl)
        losing_days = len(losing_days_pnl)
        breakeven_days = total_trading_days - winning_days - losing_days
        day_win_percentage = (Decimal(winning_days) / total_trading_days * 100) if total_trading_days > 0 else Decimal(0)
        average_daily_volume = np.mean([float(v) for v in daily_volume.values()]) if daily_volume else Decimal(0)

        sharpe = sortino = calmar = Decimal(0)
        skewness_val = kurtosis_val = Decimal(0)
        var_95 = cvar_95 = Decimal(0)
        if len(daily_pnl) > 2:
            daily_returns = np.array([float(p) for p in daily_pnl.values()])
            avg_return = np.mean(daily_returns)
            volatility = np.std(daily_returns)
            skewness_val = skew(daily_returns)
            kurtosis_val = kurtosis(daily_returns)
            sharpe = Decimal(avg_return / volatility * np.sqrt(252)) if volatility > 0 else Decimal(0)
            downside_returns = daily_returns[daily_returns < 0]
            downside_std = np.std(downside_returns) if downside_returns.any() else 0
            sortino = Decimal(avg_return / downside_std * np.sqrt(252)) if downside_std > 0 else Decimal(0)

            var_95 = Decimal(np.percentile(daily_returns, 5))
            cvar_95_returns = daily_returns[daily_returns <= float(var_95)]
            cvar_95 = Decimal(np.mean(cvar_95_returns)) if cvar_95_returns.any() else Decimal(0)

            trade_dates = sorted(daily_pnl.keys())
            if trade_dates:
                trading_days = (trade_dates[-1] - trade_dates[0]).days
                if trading_days > 0 and max_drawdown_abs > 0:
                    annualized_return = base_stats['total_pl'] * (Decimal('365') / Decimal(trading_days))
                    calmar = annualized_return / max_drawdown_abs

        streaks_stats = self._calculate_streaks_and_consistency(base_stats['pnl_data'], daily_pnl_values)

        peak_value = np.max(peak_array) if peak_array.size > 0 else 0
        max_drawdown_pct = (max_drawdown_abs / Decimal(peak_value)) * 100 if peak_value > 0 else Decimal(0)

        results = {
            'avg_sell_efficiency': np.mean(sell_efficiencies) * 100 if sell_efficiencies else Decimal(0),
            'avg_total_efficiency': np.mean(total_efficiencies) * 100 if total_efficiencies else Decimal(0),
            'avg_planned_rr': np.mean([float(r) for r in planned_rrs]) if planned_rrs else Decimal(0),
            'avg_realized_rr': np.mean([float(r) for r in realized_rrs]) if realized_rrs else Decimal(0),
            'equity_curve_data': equity_curve_data,
            'max_drawdown_abs': max_drawdown_abs,
            'max_drawdown_pct': max_drawdown_pct,
            'sharpe_ratio': sharpe, 'sortino_ratio': sortino, 'calmar_ratio': calmar,
            'skewness': Decimal(skewness_val), 'kurtosis': Decimal(kurtosis_val),
            'var_95': abs(var_95), 'cvar_95': abs(cvar_95),
            'realized_rrs_list': [float(r) for r in realized_rrs],
            'average_daily_pnl': Decimal(average_daily_pnl),
            'average_winning_day_pnl': Decimal(average_winning_day_pnl),
            'average_losing_day_pnl': Decimal(average_losing_day_pnl),
            'largest_profitable_day': largest_profitable_day,
            'largest_losing_day': largest_losing_day,
            'net_daily_pnl_chart': net_daily_pnl_chart,
            'winning_days': winning_days,
            'losing_days': losing_days,
            'breakeven_days': breakeven_days,
            'day_win_percentage': day_win_percentage,
            'average_daily_volume': Decimal(average_daily_volume),
            'recovery_factor': recovery_factor,
            'average_drawdown': Decimal(average_drawdown),
            'average_hold_time': average_hold_time,
            'longest_trade_duration': longest_trade_duration,
            'performance_by_day_of_week': performance_by_day_of_week,
            'performance_by_hour': performance_by_hour,
        }
        results.update(streaks_stats)
        return results

    def _calculate_streaks_and_consistency(self, pnl_data, daily_pnl_values):
        # Trade streaks
        max_consecutive_wins = max_consecutive_losses = 0
        current_wins = current_losses = 0
        for pnl in pnl_data:
            if pnl > 0:
                current_wins += 1
                current_losses = 0
            elif pnl < 0:
                current_losses += 1
                current_wins = 0
            else: # Breakeven resets streaks
                current_wins = current_losses = 0
            max_consecutive_wins = max(max_consecutive_wins, current_wins)
            max_consecutive_losses = max(max_consecutive_losses, current_losses)

        current_trade_streak = 0
        if pnl_data:
            # Check the streak ending with the last trade
            if pnl_data[-1] > 0:
                # Count backwards for current win streak
                s = 0
                for p in reversed(pnl_data):
                    if p > 0: s+=1
                    else: break
                current_trade_streak = s
            elif pnl_data[-1] < 0:
                # Count backwards for current loss streak
                s = 0
                for p in reversed(pnl_data):
                    if p < 0: s+=1
                    else: break
                current_trade_streak = -s

        # Day streaks
        max_consecutive_winning_days = max_consecutive_losing_days = 0
        current_winning_days = current_losing_days = 0
        for pnl in daily_pnl_values:
            if pnl > 0:
                current_winning_days += 1
                current_losing_days = 0
            elif pnl < 0:
                current_losing_days += 1
                current_winning_days = 0
            else:
                current_winning_days = current_losing_days = 0
            max_consecutive_winning_days = max(max_consecutive_winning_days, current_winning_days)
            max_consecutive_losing_days = max(max_consecutive_losing_days, current_losing_days)

        current_day_streak = 0
        if daily_pnl_values:
            if daily_pnl_values[-1] > 0:
                s = 0
                for p in reversed(daily_pnl_values):
                    if p > 0: s += 1
                    else: break
                current_day_streak = s
            elif daily_pnl_values[-1] < 0:
                s = 0
                for p in reversed(daily_pnl_values):
                    if p < 0: s += 1
                    else: break
                current_day_streak = -s

        consistency_score = np.std([float(v) for v in daily_pnl_values]) if daily_pnl_values else 0

        return {
            'max_consecutive_wins': max_consecutive_wins,
            'max_consecutive_losses': max_consecutive_losses,
            'current_trade_streak': current_trade_streak,
            'max_consecutive_winning_days': max_consecutive_winning_days,
            'max_consecutive_losing_days': max_consecutive_losing_days,
            'current_day_streak': current_day_streak,
            'consistency_score': Decimal(consistency_score)
        }

    def calculate_vantage_score(self):
        """
        Calcola il Vantage Score e i suoi componenti individuali.
        """
        if not self.all_trades:
            return {
                'vantage_score': 0, 'profit_factor_score': 0, 'avg_win_loss_score': 0,
                'max_drawdown_score': 0, 'win_rate_score': 0, 'consistency_score': 0,
                'recovery_factor_score': 0
            }

        base_stats = self._calculate_base_stats()
        advanced_stats = self._calculate_advanced_stats(base_stats)
        stats = {**base_stats, **advanced_stats}

        pf = stats.get('profit_factor', Decimal(0))
        if pf == Decimal('inf'): pf_score = 100
        elif pf >= Decimal('2.6'): pf_score = 100
        elif pf >= Decimal('2.2'): pf_score = 80
        elif pf >= Decimal('1.8'): pf_score = 60
        elif pf >= Decimal('1.5'): pf_score = 40
        elif pf > Decimal('1.0'): pf_score = 20
        else: pf_score = 0

        awl = stats.get('average_win_loss_ratio', Decimal(0))
        if awl == Decimal('inf'): awl_score = 100
        elif awl >= Decimal('2.6'): awl_score = 100
        elif awl >= Decimal('2.2'): awl_score = 80
        elif awl >= Decimal('1.8'): awl_score = 60
        elif awl >= Decimal('1.5'): awl_score = 40
        elif awl > Decimal('1.0'): awl_score = 20
        else: awl_score = 0

        max_dd_pct = float(stats.get('max_drawdown_pct', 100))
        mdd_score = max(0, 100 - max_dd_pct)

        win_rate = float(stats.get('win_rate', 0))
        wr_score = min(100, (win_rate / 60.0) * 100) if 60.0 > 0 else 0

        total_profit = float(stats.get('total_pl', 0))
        daily_std = float(stats.get('consistency_score', 0))
        consistency_score = 0
        if total_profit > 0 and daily_std > 0:
            variation = (daily_std / total_profit) * 100
            consistency_score = max(0, 100 - variation)
        elif total_profit > 0:
            consistency_score = 100

        rf = stats.get('recovery_factor', Decimal(0))
        if rf == Decimal('inf') or rf >= Decimal('3.5'): rf_score = 100
        elif rf >= Decimal('2.5'): rf_score = 80
        elif rf >= Decimal('1.8'): rf_score = 60
        elif rf >= Decimal('1.0'): rf_score = 40
        else: rf_score = 0

        vantage_score = (
            (pf_score * 0.25) + (awl_score * 0.20) + (mdd_score * 0.20) +
            (wr_score * 0.15) + (consistency_score * 0.10) + (rf_score * 0.10)
        )

        return {
            'vantage_score': round(vantage_score, 2),
            'profit_factor_score': round(pf_score, 2),
            'avg_win_loss_score': round(awl_score, 2),
            'max_drawdown_score': round(mdd_score, 2),
            'win_rate_score': round(wr_score, 2),
            'consistency_score': round(consistency_score, 2),
            'recovery_factor_score': round(rf_score, 2)
        }

    def _prepare_chart_data(self, advanced_stats):
        """Dati per grafici."""
        performance_by_setup = {}
        for t in self.all_trades:
            if hasattr(t, 'playbooks') and t.playbooks:
                for playbook in t.playbooks:
                    setup_name = playbook.title or "Non specificato"
                    performance_by_setup.setdefault(setup_name, Decimal(0))
                    performance_by_setup[setup_name] += t.net_pnl
            else:
                setup_name = "Non specificato"
                performance_by_setup.setdefault(setup_name, Decimal(0))
                performance_by_setup[setup_name] += t.net_pnl
        setup_chart_data = [{'setup': k, 'total_pl': float(v)} for k, v in performance_by_setup.items()]

        r_multiple_bins = [-np.inf, -2, -1, 0, 1, 2, 3, np.inf]
        r_multiple_labels = ["< -2R", "-2R..-1R", "-1R..0R", "0R..1R", "1R..2R", "2R..3R", "> 3R"]
        realized_rrs = advanced_stats.get('realized_rrs_list', [])
        counts, _ = np.histogram(realized_rrs, bins=r_multiple_bins)

        pnl_by_day_data = advanced_stats.get('performance_by_day_of_week', {})
        pnl_by_hour_data = advanced_stats.get('performance_by_hour', {})

        return {
            'setup_chart_data': setup_chart_data,
            'r_multiple_data': {'labels': r_multiple_labels, 'data': counts.tolist()},
            'performance_by_day': {
                'labels': list(pnl_by_day_data.keys()),
                'data': [float(v) for v in pnl_by_day_data.values()]
            },
            'performance_by_hour': {
                'labels': list(pnl_by_hour_data.keys()),
                'data': [float(v) for v in pnl_by_hour_data.values()]
            }
        }

    def calculate_equity_curve(self):
        """
        Calcola e formatta i dati per la equity curve.
        """
        if not self.all_trades:
            return {'labels': [], 'data': []}

        fallback_date = self._convert_to_local_tz(datetime(1970, 1, 1))
        self.all_trades.sort(key=lambda x: x.entry_timestamp or fallback_date)

        pnl_data = [t.net_pnl for t in self.all_trades]
        cumulative_pnl = np.cumsum([float(p) for p in pnl_data])

        labels = [
            t.entry_timestamp.strftime('%Y-%m-%d %H:%M')
            for t in self.all_trades if t.entry_timestamp
        ]

        return {'labels': labels, 'data': list(cumulative_pnl)}

    def calculate_trade_summary(self):
        """
        Calcola un riepilogo per un set di trade, includendo
        statistiche di base e la curva del P&L cumulativo.
        """
        if not self.all_trades:
            return {
                "stats": {
                    "net_pnl": 0, "trade_count": 0, "winning_trades": 0,
                    "losing_trades": 0, "breakeven_trades": 0, "gross_profit": 0,
                    "gross_loss": 0, "profit_factor": 0, "profit_factor_label": "0.00", "win_rate": 0
                },
                "cumulative_pnl_series": {"labels": [], "data": []}
            }

        base_stats = self._calculate_base_stats()
        equity_curve = self.calculate_equity_curve()

        pnl_data = base_stats['pnl_data']
        gross_profit = sum(p for p in pnl_data if p > 0)
        gross_loss = abs(sum(p for p in pnl_data if p < 0))

        profit_factor = None
        profit_factor_label = "0.00"
        if gross_loss > 0:
            pf_val = gross_profit / gross_loss
            profit_factor = float(pf_val)
            profit_factor_label = f"{pf_val:.2f}"
        elif gross_profit > 0:
            profit_factor = float('inf')
            profit_factor_label = "∞"

        win_rate = float(base_stats['win_rate'])

        summary_stats = {
            "net_pnl": float(base_stats['total_pl']),
            "trade_count": base_stats['trade_count'],
            "winning_trades": base_stats['winning_trades_count'],
            "losing_trades": base_stats['losing_trades_count'],
            "breakeven_trades": base_stats['breakeven_trades_count'],
            "gross_profit": float(gross_profit),
            "gross_loss": float(gross_loss),
            "profit_factor": profit_factor,
            "profit_factor_label": profit_factor_label,
            "win_rate": win_rate
        }

        return {
            "stats": summary_stats,
            "cumulative_pnl_series": equity_curve
        }

    def calculate_processed_stats(self):
        """
        Calcola le statistiche aggregate necessarie per la dashboard del frontend.
        """
        if not self.all_trades:
            return {
                "general_stats": {"total_pnl": 0, "trade_count": 0, "winning_trades": 0, "losing_trades": 0, "breakeven_trades": 0, "gross_profit": 0, "gross_loss": 0, "total_risk": 0},
                "daily_data": {}, "by_strategy": {}, "max_abs_pnl_by_strategy": 0.0,
                "by_day_of_week": {}, "win_loss_days": {"winning_days": 0, "losing_days": 0, "breakeven_days": 0},
                "monthly_totals": {}, "weekly_totals": {}
            }

        total_pnl = Decimal(0)
        trade_count = len(self.all_trades)
        winning_trades, losing_trades, breakeven_trades = 0, 0, 0
        gross_profit, gross_loss, total_risk = Decimal(0), Decimal(0), Decimal(0)

        daily_data, by_strategy, monthly_totals, weekly_totals = {}, {}, {}, {}
        seen_days_per_week = {}
        days_map = {0: 'Lunedì', 1: 'Martedì', 2: 'Mercoledì', 3: 'Giovedì', 4: 'Venerdì', 5: 'Sabato', 6: 'Domenica'}
        by_day_of_week = {name: {'total_pnl': Decimal(0), 'trade_count': 0, 'winning_trades': 0} for name in days_map.values()}

        for trade in self.all_trades:
            pnl = trade.net_pnl
            risk = Decimal(0)
            entry = Decimal(trade.entry_price or 0)
            sl = Decimal(trade.stop_loss_price or 0)
            size = Decimal(trade.position_size or 1)
            if entry > 0 and sl > 0:
                risk = abs(entry - sl) * size

            total_pnl += pnl
            total_risk += risk
            if pnl > 0:
                winning_trades += 1
                gross_profit += pnl
            elif pnl < 0:
                losing_trades += 1
                gross_loss += abs(pnl)
            else:
                breakeven_trades += 1

            if trade.entry_timestamp:
                day_key = trade.entry_timestamp.strftime('%Y-%m-%d')
                daily_data.setdefault(day_key, {'total_pnl': Decimal(0), 'trade_count': 0, 'winning_trades': 0})
                daily_data[day_key]['total_pnl'] += pnl
                daily_data[day_key]['trade_count'] += 1
                if pnl > 0: daily_data[day_key]['winning_trades'] += 1

                if hasattr(trade, 'playbooks') and trade.playbooks:
                    for playbook in trade.playbooks:
                        strategy = playbook.title or 'N/A'
                        by_strategy.setdefault(strategy, {'total_pnl': Decimal(0), 'trade_count': 0, 'winning_trades': 0})
                        by_strategy[strategy]['total_pnl'] += pnl
                        by_strategy[strategy]['trade_count'] += 1
                        if pnl > 0:
                            by_strategy[strategy]['winning_trades'] += 1
                else:
                    strategy = 'N/A'
                    by_strategy.setdefault(strategy, {'total_pnl': Decimal(0), 'trade_count': 0, 'winning_trades': 0})
                    by_strategy[strategy]['total_pnl'] += pnl
                    by_strategy[strategy]['trade_count'] += 1
                    if pnl > 0:
                        by_strategy[strategy]['winning_trades'] += 1

                day_name = days_map[trade.entry_timestamp.weekday()]
                by_day_of_week[day_name]['total_pnl'] += pnl
                by_day_of_week[day_name]['trade_count'] += 1
                if pnl > 0: by_day_of_week[day_name]['winning_trades'] += 1

                month_key = trade.entry_timestamp.strftime('%Y-%m')
                monthly_totals[month_key] = monthly_totals.get(month_key, Decimal(0)) + pnl

                week_key = trade.entry_timestamp.strftime('%Y-W%V')
                day_of_year = trade.entry_timestamp.timetuple().tm_yday
                weekly_totals.setdefault(week_key, {'total_pnl': Decimal(0), 'trading_days': set()})
                weekly_totals[week_key]['total_pnl'] += pnl
                weekly_totals[week_key]['trading_days'].add(day_of_year)

        for week_key, data in weekly_totals.items():
            data['trading_days'] = len(data['trading_days'])

        winning_days = sum(1 for day in daily_data.values() if day['total_pnl'] > 0)
        losing_days = sum(1 for day in daily_data.values() if day['total_pnl'] < 0)
        breakeven_days = len(daily_data) - winning_days - losing_days

        max_abs_pnl_by_strategy = float(max(abs(s['total_pnl']) for s in by_strategy.values())) if by_strategy else 0.0

        for group in [by_strategy, daily_data, by_day_of_week]:
            for stats in group.values():
                stats['win_rate'] = (stats['winning_trades'] / stats['trade_count']) * 100 if stats['trade_count'] > 0 else 0
                stats['total_pnl'] = float(stats['total_pnl'])

        return {
            "general_stats": {
                "total_pnl": float(total_pnl), "trade_count": trade_count, "winning_trades": winning_trades,
                "losing_trades": losing_trades, "breakeven_trades": breakeven_trades,
                "gross_profit": float(gross_profit), "gross_loss": float(gross_loss), "total_risk": float(total_risk)
            },
            "daily_data": daily_data,
            "by_strategy": by_strategy,
            "max_abs_pnl_by_strategy": max_abs_pnl_by_strategy,
            "by_day_of_week": by_day_of_week,
            "win_loss_days": {"winning_days": winning_days, "losing_days": losing_days, "breakeven_days": breakeven_days},
            "monthly_totals": {k: float(v) for k, v in monthly_totals.items()},
            "weekly_totals": {k: {'total_pnl': float(v['total_pnl']), 'trading_days': v['trading_days']} for k, v in weekly_totals.items()}
        }

    def calculate_all_metrics(self):
        """Pacchetto completo di metriche + grafici."""
        if not self.all_trades:
            return self._get_empty_response()

        base_stats = self._calculate_base_stats()
        advanced_stats = self._calculate_advanced_stats(base_stats)
        chart_data = self._prepare_chart_data(advanced_stats)

        final_stats = {**base_stats, **advanced_stats}
        # Rimuovi dati ridondanti o non necessari nel payload finale
        for k in ('winning_trades', 'realized_rrs_list', 'losing_trades_pnl', 'pnl_data'):
            final_stats.pop(k, None)

        # Converte tutti i Decimal in float per la serializzazione JSON
        for key, value in final_stats.items():
            if isinstance(value, Decimal):
                final_stats[key] = float(value)
            elif isinstance(value, dict):
                 for sub_key, sub_value in value.items():
                     if isinstance(sub_value, Decimal):
                         value[sub_key] = float(sub_value)

        fallback_date = self._convert_to_local_tz(datetime(1970, 1, 1))
        display_trades = sorted(
            self.all_trades,
            key=lambda x: x.entry_timestamp or fallback_date,
            reverse=True
        )

        final_payload = {
            'trades': display_trades,
            'stats': final_stats,
            'equity_curve_data': advanced_stats['equity_curve_data'],
            **chart_data
        }
        return final_payload
