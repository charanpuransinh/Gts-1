from __future__ import annotations
import importlib
from dataclasses import dataclass
from datetime import date

_types = importlib.import_module("02_instruments.instrument_types")
_master = importlib.import_module("02_instruments.instrument_master")
_builder = importlib.import_module("02_instruments.contract_builder")
_calendar = importlib.import_module("02_instruments.expiry_calendar")

InstrumentMaster = _master.InstrumentMaster
ContractBuilder = _builder.ContractBuilder
ContractBuildError = _builder.ContractBuildError

@dataclass(frozen=True)
class OptionContractContext:
    symbol: str
    exchange: str
    strike: float
    expiry: str
    option_type: str
    lot_size: int
    tick_size: float

def build_option_context(master: InstrumentMaster, symbol: str,
                         strike: float, expiry: str, option_type: str) -> OptionContractContext:
    c = ContractBuilder(master).build_option(symbol, strike, expiry, option_type)
    return OptionContractContext(c.underlying_symbol, c.exchange, c.strike,
                                 c.expiry, c.option_type, c.lot_size, c.tick_size)

def next_expiry_for_instrument(master: InstrumentMaster, symbol: str,
                               reference_date: date):
    instrument = master.get(symbol)
    return _calendar.next_expiry(reference_date, instrument.expiry_frequency)
