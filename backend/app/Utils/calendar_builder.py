import calendar
from datetime import date
from typing import List, Dict, Any

def build_calendar_structure(year: int, month: int, daily_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Builds the full calendar structure for a given month, including placeholders
    and weekly summaries, enriched with trade data.

    Args:
        year: The year for the calendar.
        month: The month for the calendar.
        daily_data: A list of dictionaries, where each dict has "date", "pnl",
                    "trade_count", and "winning_trades_count".

    Returns:
        A dictionary containing 'weeksOfDays' and 'weeklySummaries'.
    """
    # Create a lookup map for daily data
    data_map = {item['date']: item for item in daily_data}

    month_calendar = calendar.monthcalendar(year, month)

    weeks_of_days = []
    weekly_summaries = []

    # calendar.monthcalendar starts the week on Monday.
    for week_num, week in enumerate(month_calendar, 1):
        week_chunk = []
        for day_of_month in week:
            if day_of_month == 0:
                week_chunk.append({"isPlaceholder": True, "key": f"ph-{len(weeks_of_days)}-{len(week_chunk)}"})
            else:
                date_str = f"{year}-{month:02d}-{day_of_month:02d}"
                day_data = data_map.get(date_str, {"pnl": 0, "trade_count": 0, "winning_trades_count": 0})

                week_chunk.append({
                    "date": day_of_month,
                    "fullDate": date_str,
                    "dailyData": {
                        "totalPnl": day_data["pnl"],
                        "tradeCount": day_data["trade_count"],
                        "winningTrades": day_data["winning_trades_count"],
                    },
                    "isPlaceholder": False,
                    "key": date_str,
                })

        weeks_of_days.append(week_chunk)

        # Calculate weekly summary
        weekly_pnl = sum(day.get("dailyData", {}).get("totalPnl", 0) for day in week_chunk if not day["isPlaceholder"])
        trading_days_count = sum(1 for day in week_chunk if not day["isPlaceholder"] and day.get("dailyData", {}).get("tradeCount", 0) > 0)

        weekly_summaries.append({
            "weekNumber": week_num,
            "totalPnl": weekly_pnl,
            "tradingDaysCount": trading_days_count,
        })

    return {"weeksOfDays": weeks_of_days, "weeklySummaries": weekly_summaries}
