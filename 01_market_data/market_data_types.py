"""
market_data_types.py
=====================
MODULE   : 01_market_data
OWNER    : AI-1 (Market Data)
PURPOSE  : Canonical data structures used by every market-data component.
           Every other file in 01_market_data imports from here so the
           whole pipeline speaks one common "shape" of tick/bar/quote.

INPUT    : n/a (pure data definitions)
OUTPUT   : Tick, Quote, Bar, OptionQuote, MarketStatus dataclasses
CALLER   : market_data_feed.py, historical_data_fetcher.py,
           data_normalizer.py, market_data_cache.py, 03_data_engine.*
CALLEE   : none
DEPENDS  : none (stdlib only)
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any


class AssetClass(Enum):
    US_STOCK = "US_STOCK"
    US_OPTION = "US_OPTION"
    INDEX = "INDEX"
    INDEX_OPTION = "INDEX_OPTION"
    COMMODITY = "COMMODITY"
    FUTURE = "FUTURE"


class MarketState(Enum):
    PRE_OPEN = "PRE_OPEN"
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    HALTED = "HALTED"
    UNKNOWN = "UNKNOWN"


class FeedStatus(Enum):
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    RECONNECTING = "RECONNECTING"
    STALE = "STALE"        # connected but no new ticks within threshold


@dataclass
class Tick:
    """A single last-traded-price event."""
    symbol: str
    ltp: float
    ltq: int = 0                       # last traded quantity
    timestamp: float = field(default_factory=time.time)
    exchange: str = ""
    asset_class: AssetClass = AssetClass.US_STOCK
    volume: int = 0
    oi: Optional[int] = None           # open interest (F&O)


@dataclass
class Quote:
    """Best bid/ask snapshot."""
    symbol: str
    bid: float
    ask: float
    bid_qty: int = 0
    ask_qty: int = 0
    timestamp: float = field(default_factory=time.time)

    @property
    def mid(self) -> float:
        return (self.bid + self.ask) / 2.0

    @property
    def spread(self) -> float:
        return max(0.0, self.ask - self.bid)


@dataclass
class Bar:
    """OHLCV candle for a fixed interval."""
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    start_time: float
    end_time: float
    interval_seconds: int
    oi: Optional[int] = None


@dataclass
class OptionQuote:
    """Single option-chain leg snapshot (raw, pre-Greeks)."""
    symbol: str                # underlying, e.g. "NIFTY"
    strike: float
    expiry: str                 # ISO date "YYYY-MM-DD"
    option_type: str            # "CE" / "PE" / "CALL" / "PUT"
    ltp: float
    bid: float
    ask: float
    volume: int = 0
    oi: int = 0
    oi_change: int = 0
    iv: Optional[float] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class MarketStatus:
    exchange: str
    state: MarketState
    feed_status: FeedStatus
    last_tick_age_seconds: float = 0.0
    message: str = ""
    extra: Dict[str, Any] = field(default_factory=dict)
