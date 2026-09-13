"""
test_market_data_feed.py
MODULE: 01_market_data (tests)
OWNER : AI-1
Covers: SimulatedMarketDataFeed connect/subscribe/pump, callback dispatch,
        staleness detection.
"""

import sys, os, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from market_data_feed import SimulatedMarketDataFeed
from market_data_types import FeedStatus


def test_connect_sets_status_connected():
    feed = SimulatedMarketDataFeed(seed=1)
    feed.connect()
    status = feed.get_status()
    assert status.feed_status == FeedStatus.CONNECTED


def test_subscribe_and_pump_dispatches_tick():
    feed = SimulatedMarketDataFeed(seed=1)
    feed.connect()
    feed.subscribe(["NIFTY"])
    received = []
    feed.on_tick(lambda t: received.append(t))
    tick = feed.pump("NIFTY")
    assert len(received) == 1
    assert received[0].symbol == "NIFTY"
    assert received[0].ltp == tick.ltp


def test_pump_unsubscribed_symbol_raises():
    feed = SimulatedMarketDataFeed(seed=1)
    feed.connect()
    try:
        feed.pump("NOPE")
        assert False, "should have raised"
    except ValueError:
        pass


def test_unsubscribe_removes_symbol():
    feed = SimulatedMarketDataFeed(seed=1)
    feed.connect()
    feed.subscribe(["NIFTY"])
    feed.unsubscribe(["NIFTY"])
    assert "NIFTY" not in feed.subscribed_symbols


def test_stale_detection():
    feed = SimulatedMarketDataFeed(seed=1, stale_after_seconds=0.01)
    feed.connect()
    feed.subscribe(["NIFTY"])
    feed.pump("NIFTY")
    time.sleep(0.05)
    status = feed.get_status("NIFTY")
    assert status.feed_status == FeedStatus.STALE


def test_quote_has_valid_spread():
    feed = SimulatedMarketDataFeed(seed=2)
    feed.connect()
    feed.subscribe(["NIFTY"])
    feed.pump("NIFTY")
    q = feed.pump_quote("NIFTY", spread=1.0)
    assert q.ask >= q.bid
    assert q.spread == q.ask - q.bid
