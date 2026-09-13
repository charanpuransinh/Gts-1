"""
test_historical_and_cache.py
MODULE: 01_market_data (tests)
OWNER : AI-1
Covers: InMemoryHistoricalDataFetcher synthesis + validation,
        MarketDataCache read/write/staleness.
"""

import sys, os, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from historical_data_fetcher import InMemoryHistoricalDataFetcher
from market_data_cache import MarketDataCache
from market_data_types import Tick, Bar


def test_synthesized_bars_are_valid_and_ordered():
    fetcher = InMemoryHistoricalDataFetcher(seed=42)
    bars = fetcher.fetch_bars_validated("NIFTY", 60, 0, 600)
    assert len(bars) == 10
    for b in bars:
        assert b.low <= b.open <= b.high
        assert b.low <= b.close <= b.high


def test_fetch_bars_validated_rejects_bad_range():
    fetcher = InMemoryHistoricalDataFetcher(seed=1)
    try:
        fetcher.fetch_bars_validated("X", 60, 100, 50)
        assert False
    except ValueError:
        pass


def test_load_bars_returns_preloaded_data():
    fetcher = InMemoryHistoricalDataFetcher()
    bar = Bar(symbol="X", open=1, high=2, low=1, close=1.5,
              volume=10, start_time=0, end_time=60, interval_seconds=60)
    fetcher.load_bars("X", [bar])
    result = fetcher.fetch_bars("X", 60, 0, 60)
    assert len(result) == 1
    assert result[0].close == 1.5


def test_cache_ltp_lookup():
    cache = MarketDataCache()
    cache.update_tick(Tick(symbol="NIFTY", ltp=22000.0))
    assert cache.get_ltp("NIFTY") == 22000.0
    assert cache.get_ltp("UNKNOWN") is None


def test_cache_bar_window():
    cache = MarketDataCache(max_bars_per_symbol=3)
    for i in range(5):
        cache.append_bar(Bar(symbol="X", open=i, high=i, low=i, close=i,
                              volume=1, start_time=i, end_time=i + 1,
                              interval_seconds=1))
    bars = cache.get_bars("X")
    assert len(bars) == 3          # deque capped at max_bars_per_symbol
    assert bars[-1].open == 4      # most recent kept


def test_cache_staleness():
    cache = MarketDataCache()
    old_tick = Tick(symbol="X", ltp=1.0, timestamp=time.time() - 100)
    cache.update_tick(old_tick)
    assert cache.is_stale("X", max_age_seconds=1) is True
    assert cache.is_stale("MISSING", max_age_seconds=1) is True
