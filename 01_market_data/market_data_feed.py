"""
market_data_feed.py
====================
MODULE   : 01_market_data
OWNER    : AI-1 (Market Data)
PURPOSE  : Real-time market data feed abstraction. Any broker/vendor feed
           (websocket, TCP, polling) implements MarketDataFeed and pushes
           Tick/Quote/OptionQuote objects through the common callback API.
           Strategies and 03_data_engine never talk to a vendor directly —
           they only talk to this interface.

INPUT    : Raw vendor feed messages (implementation-specific)
OUTPUT   : Tick / Quote / OptionQuote callbacks, MarketStatus updates
CALLER   : 03_data_engine.*, 05_market_analysis.*, 07_strategy.*,
           20_dashboard (live ticker)
CALLEE   : market_data_types
DEPENDS  : market_data_types
"""

from __future__ import annotations
import time
import random
from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Optional, Set

from market_data_types import (
    Tick, Quote, OptionQuote, MarketStatus, MarketState, FeedStatus,
    AssetClass,
)

TickCallback = Callable[[Tick], None]
QuoteCallback = Callable[[Quote], None]
StatusCallback = Callable[[MarketStatus], None]


class MarketDataFeed(ABC):
    """
    Abstract base for a live market data connection.
    Concrete subclasses (e.g. a specific broker's websocket feed)
    must implement connect(), disconnect(), subscribe(), unsubscribe().
    """

    def __init__(self, exchange: str, stale_after_seconds: float = 15.0):
        self.exchange = exchange
        self.stale_after_seconds = stale_after_seconds
        self._tick_subscribers: List[TickCallback] = []
        self._quote_subscribers: List[QuoteCallback] = []
        self._status_subscribers: List[StatusCallback] = []
        self._subscribed_symbols: Set[str] = set()
        self._last_tick_time: Dict[str, float] = {}
        self._feed_status: FeedStatus = FeedStatus.DISCONNECTED
        self._market_state: MarketState = MarketState.UNKNOWN

    # -- lifecycle ---------------------------------------------------
    @abstractmethod
    def connect(self) -> bool:
        ...

    @abstractmethod
    def disconnect(self) -> None:
        ...

    @abstractmethod
    def subscribe(self, symbols: List[str]) -> None:
        ...

    @abstractmethod
    def unsubscribe(self, symbols: List[str]) -> None:
        ...

    # -- subscriber registration --------------------------------------
    def on_tick(self, callback: TickCallback) -> None:
        self._tick_subscribers.append(callback)

    def on_quote(self, callback: QuoteCallback) -> None:
        self._quote_subscribers.append(callback)

    def on_status(self, callback: StatusCallback) -> None:
        self._status_subscribers.append(callback)

    # -- dispatch helpers (called by subclasses on new data) ----------
    def _dispatch_tick(self, tick: Tick) -> None:
        self._last_tick_time[tick.symbol] = tick.timestamp
        for cb in self._tick_subscribers:
            cb(tick)

    def _dispatch_quote(self, quote: Quote) -> None:
        for cb in self._quote_subscribers:
            cb(quote)

    def _set_status(self, feed_status: FeedStatus, message: str = "") -> None:
        self._feed_status = feed_status
        status = MarketStatus(
            exchange=self.exchange,
            state=self._market_state,
            feed_status=feed_status,
            message=message,
        )
        for cb in self._status_subscribers:
            cb(status)

    # -- health --------------------------------------------------------
    def get_status(self, symbol: Optional[str] = None) -> MarketStatus:
        age = 0.0
        if symbol and symbol in self._last_tick_time:
            age = time.time() - self._last_tick_time[symbol]
        feed_status = self._feed_status
        if feed_status == FeedStatus.CONNECTED and age > self.stale_after_seconds and symbol:
            feed_status = FeedStatus.STALE
        return MarketStatus(
            exchange=self.exchange,
            state=self._market_state,
            feed_status=feed_status,
            last_tick_age_seconds=age,
        )

    @property
    def subscribed_symbols(self) -> Set[str]:
        return set(self._subscribed_symbols)


class SimulatedMarketDataFeed(MarketDataFeed):
    """
    Deterministic, dependency-free feed used for tests, backtesting
    scaffolding, and local development when no live broker connection
    is available. Generates a synthetic random-walk tick per symbol
    each time `pump()` is called (no background threads).
    """

    def __init__(self, exchange: str = "SIM", seed: Optional[int] = None,
                 start_price: float = 100.0, stale_after_seconds: float = 15.0):
        super().__init__(exchange, stale_after_seconds)
        self._rng = random.Random(seed)
        self._prices: Dict[str, float] = {}
        self._start_price = start_price

    def connect(self) -> bool:
        self._market_state = MarketState.OPEN
        self._set_status(FeedStatus.CONNECTED, "simulated feed connected")
        return True

    def disconnect(self) -> None:
        self._set_status(FeedStatus.DISCONNECTED, "simulated feed disconnected")

    def subscribe(self, symbols: List[str]) -> None:
        for s in symbols:
            self._subscribed_symbols.add(s)
            self._prices.setdefault(s, self._start_price)

    def unsubscribe(self, symbols: List[str]) -> None:
        for s in symbols:
            self._subscribed_symbols.discard(s)
            self._prices.pop(s, None)

    def pump(self, symbol: str, volatility: float = 0.5) -> Tick:
        """Advance one synthetic tick for `symbol` and dispatch it."""
        if symbol not in self._subscribed_symbols:
            raise ValueError(f"{symbol} is not subscribed")
        prev = self._prices[symbol]
        move = self._rng.uniform(-volatility, volatility)
        new_price = max(0.01, round(prev + move, 2))
        self._prices[symbol] = new_price
        tick = Tick(
            symbol=symbol,
            ltp=new_price,
            ltq=self._rng.randint(1, 100),
            exchange=self.exchange,
            volume=self._rng.randint(100, 10000),
        )
        self._dispatch_tick(tick)
        return tick

    def pump_quote(self, symbol: str, spread: float = 0.5) -> Quote:
        price = self._prices.get(symbol, self._start_price)
        quote = Quote(
            symbol=symbol,
            bid=round(price - spread / 2, 2),
            ask=round(price + spread / 2, 2),
            bid_qty=self._rng.randint(1, 500),
            ask_qty=self._rng.randint(1, 500),
        )
        self._dispatch_quote(quote)
        return quote
