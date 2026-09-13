"""
instrument_master.py
=====================
MODULE   : 02_instruments
OWNER    : AI-2 (Instruments)
PURPOSE  : Single source of truth for every tradable underlying in the
           system. Loaded once at startup (from a config file, DB, or
           vendor master-contract file in a real deployment) and then
           queried in-memory by every other module.

INPUT    : Instrument objects (registered at startup / via load_from_dicts)
OUTPUT   : Instrument lookups by symbol / exchange / segment
CALLER   : contract_builder.py, expiry_calendar.py, 06_options_engine.*,
           07_strategy.*, 12_risk.*, 14_execution.order_validator
CALLEE   : instrument_types
DEPENDS  : instrument_types
"""

from __future__ import annotations
from typing import Dict, List, Optional

from instrument_types import Instrument, SegmentType


class InstrumentNotFoundError(KeyError):
    pass


class InstrumentMaster:
    def __init__(self):
        self._by_symbol: Dict[str, Instrument] = {}

    def register(self, instrument: Instrument) -> None:
        self._by_symbol[instrument.symbol] = instrument

    def register_many(self, instruments: List[Instrument]) -> None:
        for inst in instruments:
            self.register(inst)

    def get(self, symbol: str) -> Instrument:
        try:
            return self._by_symbol[symbol]
        except KeyError as e:
            raise InstrumentNotFoundError(f"unknown instrument: {symbol}") from e

    def exists(self, symbol: str) -> bool:
        return symbol in self._by_symbol

    def find_by_segment(self, segment: SegmentType) -> List[Instrument]:
        return [i for i in self._by_symbol.values() if i.segment == segment]

    def find_by_exchange(self, exchange: str) -> List[Instrument]:
        return [i for i in self._by_symbol.values() if i.exchange == exchange]

    def tradable_symbols(self) -> List[str]:
        return [s for s, i in self._by_symbol.items() if i.is_tradable]

    def deactivate(self, symbol: str) -> None:
        inst = self.get(symbol)
        inst.is_tradable = False

    def all(self) -> List[Instrument]:
        return list(self._by_symbol.values())


def default_instrument_master() -> InstrumentMaster:
    """
    Convenience factory pre-loaded with the underlyings named in the
    GTS Master Blueprint (section 2 - MARKETS), using representative
    real-world contract specs. In production, replace this with a
    loader that reads the actual broker/exchange master-contract file.
    """
    from instrument_types import ExpiryFrequency

    master = InstrumentMaster()
    master.register_many([
        Instrument("NIFTY", "NSE", SegmentType.INDEX_OPTION,
                   lot_size=25, tick_size=0.05,
                   expiry_frequency=ExpiryFrequency.WEEKLY, strike_step=50),
        Instrument("BANKNIFTY", "NSE", SegmentType.INDEX_OPTION,
                   lot_size=15, tick_size=0.05,
                   expiry_frequency=ExpiryFrequency.WEEKLY, strike_step=100),
        Instrument("CRUDEOIL", "MCX", SegmentType.COMMODITY_FUTURE,
                   lot_size=100, tick_size=1.0,
                   expiry_frequency=ExpiryFrequency.MONTHLY),
        Instrument("NATURALGAS", "MCX", SegmentType.COMMODITY_FUTURE,
                   lot_size=1250, tick_size=0.1,
                   expiry_frequency=ExpiryFrequency.MONTHLY),
        Instrument("GOLD", "MCX", SegmentType.COMMODITY_FUTURE,
                   lot_size=100, tick_size=1.0,
                   expiry_frequency=ExpiryFrequency.MONTHLY),
        Instrument("SILVER", "MCX", SegmentType.COMMODITY_FUTURE,
                   lot_size=30, tick_size=1.0,
                   expiry_frequency=ExpiryFrequency.MONTHLY),
        Instrument("COPPER", "MCX", SegmentType.COMMODITY_FUTURE,
                   lot_size=2500, tick_size=0.05,
                   expiry_frequency=ExpiryFrequency.MONTHLY),
        Instrument("AAPL", "NASDAQ", SegmentType.EQUITY,
                   lot_size=1, tick_size=0.01,
                   expiry_frequency=ExpiryFrequency.NONE),
        # AAPL options kept under a distinct internal symbol to avoid a
        # symbol collision with the AAPL equity entry above (same
        # underlying, different segment/lot-size/expiry rules).
        Instrument("AAPL_OPT", "NASDAQ", SegmentType.EQUITY_OPTION,
                   lot_size=100, tick_size=0.01,
                   expiry_frequency=ExpiryFrequency.WEEKLY, strike_step=5),
    ])
    return master
