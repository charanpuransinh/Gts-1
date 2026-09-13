"""
market_data_cache.py
=====================
MODULE   : 01_market_data
OWNER    : AI-1 (Market Data)
PURPOSE  : Thread-unsafe (single-process, single-loop) in-memory store of
           the latest Tick/Quote per symbol plus a rolling bar buffer.
           This is the "current state of the market" that strategies,
           risk checks, and the dashboard read from — nobody should poll
           a broker directly for "what's the price right now".

INPUT    : Tick, Quote, Bar objects (usually pushed by market_data_feed)
OUTPUT   : latest Tick/Quote lookups, rolling bar windows
CALLER   : 04_indicators.*, 05_market_analysis.*, 07_strategy.*,
           12_risk.risk_engine (mark-to-market price lookup)
CALLEE   : market_data_types
DEPENDS  : market_data_types
"""

from __future__ import annotations
import time
from collections import deque
from typing import Deque, Dict, List, Optional

from market_data_types import Tick, Quote, Bar, OptionQuote


class MarketDataCache:
    def __init__(self, max_bars_per_symbol: int = 500):
        self._max_bars = max_bars_per_symbol
        self._latest_tick: Dict[str, Tick] = {}
        self._latest_quote: Dict[str, Quote] = {}
        self._latest_option: Dict[str, OptionQuote] = {}  # key: symbol|strike|expiry|type
        self._bars: Dict[str, Deque[Bar]] = {}

    # -- writes ---------------------------------------------------------
    def update_tick(self, tick: Tick) -> None:
        self._latest_tick[tick.symbol] = tick

    def update_quote(self, quote: Quote) -> None:
        self._latest_quote[quote.symbol] = quote

    def update_option_quote(self, oq: OptionQuote) -> None:
        key = f"{oq.symbol}|{oq.strike}|{oq.expiry}|{oq.option_type}"
        self._latest_option[key] = oq

    def append_bar(self, bar: Bar) -> None:
        buf = self._bars.setdefault(bar.symbol, deque(maxlen=self._max_bars))
        buf.append(bar)

    # -- reads ------------------------------------------------------------
    def get_ltp(self, symbol: str) -> Optional[float]:
        tick = self._latest_tick.get(symbol)
        return tick.ltp if tick else None

    def get_tick(self, symbol: str) -> Optional[Tick]:
        return self._latest_tick.get(symbol)

    def get_quote(self, symbol: str) -> Optional[Quote]:
        return self._latest_quote.get(symbol)

    def get_option_quote(self, symbol: str, strike: float, expiry: str,
                          option_type: str) -> Optional[OptionQuote]:
        key = f"{symbol}|{strike}|{expiry}|{option_type}"
        return self._latest_option.get(key)

    def get_bars(self, symbol: str, n: Optional[int] = None) -> List[Bar]:
        buf = self._bars.get(symbol)
        if not buf:
            return []
        if n is None:
            return list(buf)
        return list(buf)[-n:]

    def is_stale(self, symbol: str, max_age_seconds: float) -> bool:
        tick = self._latest_tick.get(symbol)
        if tick is None:
            return True
        return (time.time() - tick.timestamp) > max_age_seconds

    def symbols(self) -> List[str]:
        return list(self._latest_tick.keys())

    def clear(self) -> None:
        self._latest_tick.clear()
        self._latest_quote.clear()
        self._latest_option.clear()
        self._bars.clear()
