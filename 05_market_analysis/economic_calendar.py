from typing import Dict, List, Any
from datetime import datetime


class EconomicCalendarEngine:
    """हाई-इम्पैक्ट न्यूज़/मैक्रो इवेंट्स के दौरान वोलेटिलिटी फ़्लैग जनरेट करना"""

    def __init__(self, scheduled_events: List[Dict[str, Any]] = None):
        self.events = scheduled_events or []

    def check_event_risk(self, current_dt_utc: datetime, buffer_mins: int = 30) -> Dict[str, Any]:
        active_flags = []
        trade_restriction = "NORMAL"

        for ev in self.events:
            ev_time = ev["datetime_utc"]
            time_diff_mins = (ev_time - current_dt_utc).total_seconds() / 60.0

            if -buffer_mins <= time_diff_mins <= buffer_mins:
                active_flags.append({
                    "event_name": ev["name"], "impact": ev.get("impact", "HIGH"),
                    "mins_to_event": round(time_diff_mins, 1)
                })
                trade_restriction = "EVENT_PAUSE_HIGH_VOLATILITY"

        return {"has_event_risk": len(active_flags) > 0, "trade_restriction": trade_restriction, "active_events": active_flags}
