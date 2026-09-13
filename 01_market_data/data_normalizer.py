"""
data_normalizer.py
===================
MODULE   : 01_market_data
OWNER    : AI-1 (Market Data)
PURPOSE  : Converts raw, vendor-specific dict/JSON payloads into the
           canonical Tick / Bar / OptionQuote shapes defined in
           market_data_types.py. Every vendor adapter has different
           field names (e.g. "ltp" vs "last_price" vs "c"); this file
           is the single place that mapping lives, so 03_data_engine
           and everything downstream only ever sees canonical objects.

INPUT    : raw dict payloads from a broker/vendor feed or CSV row
OUTPUT   : Tick, Bar, OptionQuote
CALLER   : market_data_feed.py (vendor subclasses), 03_data_engine.*
CALLEE   : market_data_types
DEPENDS  : market_data_types
"""

from __future__ import annotations
from typing import Any, Dict, Optional

from market_data_types import Tick, Bar, OptionQuote, AssetClass


class NormalizationError(ValueError):
    """Raised when a raw payload is missing required fields or malformed."""


def _get_first(raw: Dict[str, Any], *keys: str) -> Any:
    for k in keys:
        if k in raw and raw[k] is not None:
            return raw[k]
    return None


def normalize_tick(raw: Dict[str, Any], exchange: str = "",
                    asset_class: AssetClass = AssetClass.US_STOCK) -> Tick:
    """
    Accepts common field-name variants across vendors:
      price   -> ltp | last_price | c | close
      symbol  -> symbol | tsym | ticker
      qty     -> ltq | last_qty | vol_traded_today (fallback)
      time    -> timestamp | ts | exchange_timestamp
    """
    symbol = _get_first(raw, "symbol", "tsym", "ticker")
    price = _get_first(raw, "ltp", "last_price", "c", "close")
    if symbol is None:
        raise NormalizationError("tick payload missing symbol field")
    if price is None:
        raise NormalizationError(f"tick payload for {symbol} missing price field")

    try:
        price = float(price)
    except (TypeError, ValueError) as e:
        raise NormalizationError(f"tick price not numeric for {symbol}: {price}") from e
    if price < 0:
        raise NormalizationError(f"negative price for {symbol}: {price}")

    kwargs = dict(symbol=str(symbol), ltp=price, exchange=exchange, asset_class=asset_class)

    qty = _get_first(raw, "ltq", "last_qty")
    if qty is not None:
        kwargs["ltq"] = int(qty)

    ts = _get_first(raw, "timestamp", "ts", "exchange_timestamp")
    if ts is not None:
        kwargs["timestamp"] = float(ts)

    vol = _get_first(raw, "volume", "vol_traded_today", "vol")
    if vol is not None:
        kwargs["volume"] = int(vol)

    oi = _get_first(raw, "oi", "open_interest")
    if oi is not None:
        kwargs["oi"] = int(oi)

    return Tick(**kwargs)


def normalize_bar(raw: Dict[str, Any], interval_seconds: int) -> Bar:
    symbol = _get_first(raw, "symbol", "tsym", "ticker")
    o = _get_first(raw, "open", "o")
    h = _get_first(raw, "high", "h")
    l = _get_first(raw, "low", "l")
    c = _get_first(raw, "close", "c")
    v = _get_first(raw, "volume", "v", "vol")
    start = _get_first(raw, "start_time", "time", "timestamp", "t")

    missing = [name for name, val in
               [("symbol", symbol), ("open", o), ("high", h),
                ("low", l), ("close", c), ("start_time", start)]
               if val is None]
    if missing:
        raise NormalizationError(f"bar payload missing fields: {missing}")

    o, h, l, c = float(o), float(h), float(l), float(c)
    if h < l:
        raise NormalizationError(f"{symbol}: high < low in raw bar")
    if not (l <= o <= h) or not (l <= c <= h):
        raise NormalizationError(f"{symbol}: open/close outside high-low range")

    start = float(start)
    return Bar(
        symbol=str(symbol), open=o, high=h, low=l, close=c,
        volume=int(v) if v is not None else 0,
        start_time=start, end_time=start + interval_seconds,
        interval_seconds=interval_seconds,
    )


def normalize_option_quote(raw: Dict[str, Any]) -> OptionQuote:
    symbol = _get_first(raw, "symbol", "underlying")
    strike = _get_first(raw, "strike", "strike_price")
    expiry = _get_first(raw, "expiry", "expiry_date")
    opt_type = _get_first(raw, "option_type", "type", "right")
    ltp = _get_first(raw, "ltp", "last_price")

    missing = [name for name, val in
               [("symbol", symbol), ("strike", strike),
                ("expiry", expiry), ("option_type", opt_type), ("ltp", ltp)]
               if val is None]
    if missing:
        raise NormalizationError(f"option quote missing fields: {missing}")

    opt_type = str(opt_type).upper()
    if opt_type in ("C", "CALL"):
        opt_type = "CE"
    elif opt_type in ("P", "PUT"):
        opt_type = "PE"

    return OptionQuote(
        symbol=str(symbol),
        strike=float(strike),
        expiry=str(expiry),
        option_type=opt_type,
        ltp=float(ltp),
        bid=float(_get_first(raw, "bid", "bid_price") or 0.0),
        ask=float(_get_first(raw, "ask", "ask_price") or 0.0),
        volume=int(_get_first(raw, "volume", "vol") or 0),
        oi=int(_get_first(raw, "oi", "open_interest") or 0),
        oi_change=int(_get_first(raw, "oi_change") or 0),
        iv=float(raw["iv"]) if raw.get("iv") is not None else None,
    )
