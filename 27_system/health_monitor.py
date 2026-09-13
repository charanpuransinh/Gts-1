
from __future__ import annotations
import time

class HealthMonitor:
    def __init__(self, feed=None) -> None:
        self.feed = feed
        self.started_at = time.time()

    def status(self) -> dict:
        result = {
            "system": "GTS",
            "component": "AI-1",
            "status": "UP",
            "uptime_seconds": round(time.time() - self.started_at, 3),
        }
        if self.feed is not None:
            s = self.feed.get_status()
            result["feed_status"] = s.feed_status.value
            result["market_state"] = s.state.value
            result["exchange"] = s.exchange
        return result
