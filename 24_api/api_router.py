
from __future__ import annotations
import json
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
MARKET = ROOT / "01_market_data"
if str(MARKET) not in sys.path:
    sys.path.insert(0, str(MARKET))

from market_data_cache import MarketDataCache
from market_data_feed import SimulatedMarketDataFeed

class AIRouter:
    def __init__(self) -> None:
        self.feed = SimulatedMarketDataFeed(exchange="SIM", seed=1)
        self.cache = MarketDataCache()
        self.feed.on_tick(self.cache.update_tick)
        self.feed.on_quote(self.cache.update_quote)
        self.feed.connect()
        self.feed.subscribe(["NIFTY"])
        self.feed.pump("NIFTY")

    def handle(self, path: str) -> tuple[int, dict]:
        parsed = urlparse(path)
        if parsed.path == "/health":
            return 200, {"system": "GTS", "component": "AI-1", "status": "UP"}
        if parsed.path == "/market/status":
            s = self.feed.get_status()
            return 200, {
                "exchange": s.exchange,
                "state": s.state.value,
                "feed_status": s.feed_status.value,
            }
        if parsed.path == "/market/tick":
            symbol = parse_qs(parsed.query).get("symbol", [""])[0].strip()
            if not symbol:
                return 400, {"error": "symbol query parameter is required"}
            if symbol not in self.feed.subscribed_symbols:
                return 404, {"error": "symbol not subscribed: " + symbol}
            tick = self.cache.get_tick(symbol)
            if tick is None:
                return 404, {"error": "no tick available: " + symbol}
            return 200, {
                "symbol": tick.symbol, "ltp": tick.ltp, "ltq": tick.ltq,
                "timestamp": tick.timestamp, "exchange": tick.exchange,
                "volume": tick.volume,
            }
        return 404, {"error": "not found"}

    @staticmethod
    def encode(payload: dict) -> bytes:
        return json.dumps(payload, sort_keys=True).encode("utf-8")
