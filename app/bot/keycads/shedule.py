from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta


class ScheduleFuncs:

    @staticmethod
    def get_dates_payload() -> List[Dict[str, Any]]:
        weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        dates_payload = []
        now = datetime.now(timezone(timedelta(hours=3))).date()

        for i in range(7):
            date = now + timedelta(days=i)
            
            raw_date = date.strftime("%Y-%m-%d")
            readable_date = date.strftime(f"{weekdays[date.weekday()]} (%d.%m)")

            dates_payload.append(
                {
                    "raw": raw_date,
                    "readable": readable_date
                }
            )

        return dates_payload


schedule_funcs =ScheduleFuncs()