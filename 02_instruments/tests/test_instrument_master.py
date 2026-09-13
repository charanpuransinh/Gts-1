"""
test_instrument_master.py
MODULE: 02_instruments (tests)
OWNER : AI-2
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from instrument_master import (
    InstrumentMaster, InstrumentNotFoundError, default_instrument_master,
)
from instrument_types import Instrument, SegmentType, ExpiryFrequency


def test_register_and_get():
    master = InstrumentMaster()
    inst = Instrument("NIFTY", "NSE", SegmentType.INDEX_OPTION, lot_size=25)
    master.register(inst)
    assert master.get("NIFTY") is inst


def test_get_unknown_raises():
    master = InstrumentMaster()
    try:
        master.get("GHOST")
        assert False
    except InstrumentNotFoundError:
        pass


def test_default_master_has_expected_symbols():
    master = default_instrument_master()
    for sym in ["NIFTY", "BANKNIFTY", "CRUDEOIL", "NATURALGAS", "GOLD", "SILVER", "COPPER"]:
        assert master.exists(sym), f"missing {sym}"


def test_default_master_no_symbol_collision():
    master = default_instrument_master()
    assert master.exists("AAPL")
    assert master.exists("AAPL_OPT")
    aapl_eq = master.get("AAPL")
    aapl_opt = master.get("AAPL_OPT")
    assert aapl_eq.segment == SegmentType.EQUITY
    assert aapl_opt.segment == SegmentType.EQUITY_OPTION


def test_find_by_segment():
    master = default_instrument_master()
    commodities = master.find_by_segment(SegmentType.COMMODITY_FUTURE)
    symbols = {i.symbol for i in commodities}
    assert "GOLD" in symbols and "CRUDEOIL" in symbols


def test_round_to_tick():
    inst = Instrument("X", "NSE", SegmentType.EQUITY, tick_size=0.05)
    assert inst.round_to_tick(100.03) == 100.05
    assert inst.round_to_tick(100.02) == 100.0


def test_is_valid_lots():
    inst = Instrument("NIFTY", "NSE", SegmentType.INDEX_OPTION, lot_size=25)
    assert inst.is_valid_lots(25) is True
    assert inst.is_valid_lots(50) is True
    assert inst.is_valid_lots(30) is False
    assert inst.is_valid_lots(0) is False


def test_deactivate_removes_from_tradable():
    master = default_instrument_master()
    master.deactivate("GOLD")
    assert "GOLD" not in master.tradable_symbols()
    assert master.exists("GOLD")  # still registered, just not tradable
