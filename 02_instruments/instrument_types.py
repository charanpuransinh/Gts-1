"""
instrument_types.py
====================
MODULE   : 02_instruments
OWNER    : AI-2 (Instruments)
PURPOSE  : Canonical definitions of a tradable instrument and its
           contract specification (lot size, tick size, expiry, strike
           step, margin multiplier). Every other module that needs to
           know "how much is 1 lot" or "what's the minimum price move"
           reads it from here — never hardcoded elsewhere.

INPUT    : n/a (pure data definitions)
OUTPUT   : Instrument, OptionContractSpec, FutureContractSpec dataclasses
CALLER   : instrument_master.py, contract_builder.py, expiry_calendar.py,
           06_options_engine.*, 12_risk.position_sizing,
           14_execution.order_validator
CALLEE   : none
DEPENDS  : none (stdlib only)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class SegmentType(Enum):
    EQUITY = "EQUITY"
    EQUITY_OPTION = "EQUITY_OPTION"
    EQUITY_FUTURE = "EQUITY_FUTURE"
    INDEX_OPTION = "INDEX_OPTION"
    INDEX_FUTURE = "INDEX_FUTURE"
    COMMODITY_FUTURE = "COMMODITY_FUTURE"
    COMMODITY_OPTION = "COMMODITY_OPTION"


class ExpiryFrequency(Enum):
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    NONE = "NONE"          # e.g. plain equities have no expiry


@dataclass
class Instrument:
    """
    Base tradable instrument — an underlying (stock/index/commodity) or
    a fully-specified derivative contract, depending on segment.
    """
    symbol: str                     # canonical internal symbol, e.g. "NIFTY"
    exchange: str                   # "NSE", "BSE", "NASDAQ", "MCX", ...
    segment: SegmentType
    lot_size: int = 1
    tick_size: float = 0.05
    expiry_frequency: ExpiryFrequency = ExpiryFrequency.NONE
    strike_step: Optional[float] = None      # only for options underlyings
    currency: str = "INR"
    is_tradable: bool = True

    def round_to_tick(self, price: float) -> float:
        if self.tick_size <= 0:
            return price
        steps = round(price / self.tick_size)
        return round(steps * self.tick_size, 8)

    def is_valid_lots(self, quantity: int) -> bool:
        return quantity > 0 and quantity % self.lot_size == 0


@dataclass
class OptionContractSpec:
    """A fully-specified option contract, derived from an underlying Instrument."""
    underlying_symbol: str
    exchange: str
    strike: float
    expiry: str                     # ISO date "YYYY-MM-DD"
    option_type: str                # "CE" / "PE"
    lot_size: int
    tick_size: float = 0.05

    @property
    def trading_symbol(self) -> str:
        return f"{self.underlying_symbol}{self.expiry.replace('-', '')}{int(self.strike)}{self.option_type}"


@dataclass
class FutureContractSpec:
    """A fully-specified futures contract, derived from an underlying Instrument."""
    underlying_symbol: str
    exchange: str
    expiry: str
    lot_size: int
    tick_size: float = 0.05

    @property
    def trading_symbol(self) -> str:
        return f"{self.underlying_symbol}{self.expiry.replace('-', '')}FUT"
