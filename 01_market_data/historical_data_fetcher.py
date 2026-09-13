"""
historical_data_fetcher.py
===========================
MODULE   : 01_market_data
OWNER    : AI-1 (Market Data)
PURPOSE  : Fetches historical OHLCV bars for a symbol over a date range,
           for any of the supported markets (US stocks/options, NIFTY,
           commodities). Abstract base so a real vendor adapter (broker
           API, data vendor, CSV archive) can be swapped in without
           touching any caller.

INPUT    : symbol, interval, start/end timestamps
OUTPUT   : List[Bar]
CALLER   : 09_backtest.backtest_engine, 04_indicators.*,
           05_market_analysis.*, 10_optimization.walk_forward
CALLEE   : market_data_types
DEPENDS  : market_data_types
"""

from __future__ import annotations
import random
from abc import ABC, abstractmethod
from typing import List, Optional

from market_data_types import Bar


class HistoricalDataFetcher(ABC):
    """Abstract interface every concrete historical data source implements."""

    @abstractmethod
    def fetch_bars(self, symbol: str, interval_seconds: int,
                    start_time: float, end_time: float) -> List[Bar]:
        ...

    def fetch_bars_validated(self, symbol: str, interval_seconds: int,
                              start_time: float, end_time: float) -> List[Bar]:
        """
        Wraps fetch_bars() with basic sanity checks so a broken vendor
        response can't silently corrupt a backtest.
        """
        if start_time >= end_time:
            raise ValueError("start_time must be before end_time")
        if interval_seconds <= 0:
            raise ValueError("interval_seconds must be positive")

        bars = self.fetch_bars(symbol, interval_seconds, start_time, end_time)

        prev_end = None
        for bar in bars:
            if bar.high < bar.low:
                raise ValueError(f"{symbol}: bar high < low at {bar.start_time}")
            if not (bar.low <= bar.open <= bar.high):
                raise ValueError(f"{symbol}: open outside [low, high] at {bar.start_time}")
            if not (bar.low <= bar.close <= bar.high):
                raise ValueError(f"{symbol}: close outside [low, high] at {bar.start_time}")
            if bar.volume < 0:
                raise ValueError(f"{symbol}: negative volume at {bar.start_time}")
            if prev_end is not None and bar.start_time < prev_end:
                raise ValueError(f"{symbol}: overlapping/out-of-order bars at {bar.start_time}")
            prev_end = bar.end_time
        return bars


class InMemoryHistoricalDataFetcher(HistoricalDataFetcher):
    """
    Simple fetcher backed by a pre-loaded dict of bars, and/or a
    deterministic synthetic generator when no real bars are loaded.
    Useful for tests and offline development.
    """

    def __init__(self, seed: Optional[int] = None):
        self._store: dict[str, List[Bar]] = {}
        self._rng = random.Random(seed)

    def load_bars(self, symbol: str, bars: List[Bar]) -> None:
        self._store[symbol] = sorted(bars, key=lambda b: b.start_time)

    def fetch_bars(self, symbol: str, interval_seconds: int,
                    start_time: float, end_time: float) -> List[Bar]:
        if symbol in self._store:
            return [
                b for b in self._store[symbol]
                if b.interval_seconds == interval_seconds
                and b.start_time >= start_time
                and b.end_time <= end_time
            ]
        # no pre-loaded data -> synthesize a deterministic random walk
        return self._synthesize(symbol, interval_seconds, start_time, end_time)

    def _synthesize(self, symbol: str, interval_seconds: int,
                     start_time: float, end_time: float) -> List[Bar]:
        bars: List[Bar] = []
        t = start_time
        price = 100.0
        while t + interval_seconds <= end_time:
            o = price
            move = self._rng.uniform(-1.0, 1.0)
            c = max(0.01, round(o + move, 2))
            h = max(o, c) + abs(self._rng.uniform(0, 0.5))
            l = min(o, c) - abs(self._rng.uniform(0, 0.5))
            bars.append(Bar(
                symbol=symbol, open=round(o, 2), high=round(h, 2),
                low=round(max(0.01, l), 2), close=c,
                volume=self._rng.randint(100, 5000),
                start_time=t, end_time=t + interval_seconds,
                interval_seconds=interval_seconds,
            ))
            price = c
            t += interval_seconds
        return bars
