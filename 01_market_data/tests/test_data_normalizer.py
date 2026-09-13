"""
test_data_normalizer.py
MODULE: 01_market_data (tests)
OWNER : AI-1
Covers: field-name variant handling, validation errors on bad payloads.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data_normalizer import (
    normalize_tick, normalize_bar, normalize_option_quote, NormalizationError,
)


def test_normalize_tick_standard_fields():
    tick = normalize_tick({"symbol": "NIFTY", "ltp": 22000.5})
    assert tick.symbol == "NIFTY"
    assert tick.ltp == 22000.5


def test_normalize_tick_alternate_field_names():
    tick = normalize_tick({"tsym": "AAPL", "last_price": 190.2, "vol_traded_today": 500})
    assert tick.symbol == "AAPL"
    assert tick.ltp == 190.2
    assert tick.volume == 500


def test_normalize_tick_missing_symbol_raises():
    try:
        normalize_tick({"ltp": 100})
        assert False
    except NormalizationError:
        pass


def test_normalize_tick_negative_price_raises():
    try:
        normalize_tick({"symbol": "X", "ltp": -5})
        assert False
    except NormalizationError:
        pass


def test_normalize_bar_valid():
    bar = normalize_bar(
        {"symbol": "NIFTY", "open": 100, "high": 105, "low": 99, "close": 102,
         "volume": 1000, "start_time": 1000.0},
        interval_seconds=60,
    )
    assert bar.high == 105
    assert bar.end_time == 1060.0


def test_normalize_bar_high_low_inverted_raises():
    try:
        normalize_bar(
            {"symbol": "X", "open": 100, "high": 90, "low": 95, "close": 92,
             "start_time": 0},
            interval_seconds=60,
        )
        assert False
    except NormalizationError:
        pass


def test_normalize_option_quote_call_put_aliases():
    oq = normalize_option_quote({
        "symbol": "NIFTY", "strike": 22000, "expiry": "2026-09-25",
        "option_type": "CALL", "ltp": 150.5,
    })
    assert oq.option_type == "CE"
