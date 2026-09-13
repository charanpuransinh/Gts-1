from typing import Dict, Any, Optional
from datetime import datetime, time, timezone, timedelta


class MarketHoursEngine:
    """टाइमज़ोन, मार्केट्स सेशंस (NSE, MCX, NYSE) और लिक्विडिटी ओवरलैप ट्रैकर"""

    def get_market_status(self, current_utc: Optional[datetime] = None) -> Dict[str, Any]:
        now = current_utc or datetime.now(timezone.utc)
        ist_now = now + timedelta(hours=5, minutes=30)
        ist_time = ist_now.time()

        nse_open = time(9, 15) <= ist_time <= time(15, 30) and ist_now.weekday() < 5
        mcx_open = time(9, 0) <= ist_time <= time(23, 30) and ist_now.weekday() < 5

        # US session (~19:00-02:30 IST) crosses midnight IST, so its weekday validity must be
        # checked against the SESSION's actual trading day, not the raw IST clock window.
        # BUG FIX: original version had no weekday check at all for the US session, which meant
        # Sunday evening IST (which is Sunday morning US, market closed) was wrongly flagged open.
        if ist_time >= time(19, 0):
            us_open = ist_now.weekday() < 5  # evening leg: valid only if IST day is Mon-Fri
        elif ist_time <= time(2, 30):
            prev_weekday = (ist_now.weekday() - 1) % 7
            us_open = prev_weekday < 5  # early-morning leg: continuation of previous evening's session
        else:
            us_open = False

        liquidity_window = "THIN_OFF_HOURS"
        if nse_open and time(13, 30) <= ist_time <= time(15, 30):
            liquidity_window = "INDIAN_EXPIRY_HIGH_LIQUIDITY_CLOSING"
        elif nse_open and us_open:
            liquidity_window = "US_INDIA_OVERLAP_WINDOW"
        elif nse_open or mcx_open or us_open:
            liquidity_window = "STANDARD_TRADING_HOURS"

        return {
            "ist_time": ist_now.strftime("%Y-%m-%d %H:%M:%S"),
            "nse_active": nse_open, "mcx_active": mcx_open, "us_active": us_open,
            "liquidity_window": liquidity_window
        }
