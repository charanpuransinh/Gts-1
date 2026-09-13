"""
test_contract_builder.py
MODULE: 02_instruments (tests)
OWNER : AI-2
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from contract_builder import ContractBuilder, ContractBuildError
from instrument_master import default_instrument_master


def make_builder():
    return ContractBuilder(default_instrument_master())


def test_build_option_valid_strike():
    builder = make_builder()
    contract = builder.build_option("NIFTY", 22000, "2026-09-25", "CE")
    assert contract.strike == 22000
    assert contract.option_type == "CE"
    assert contract.lot_size == 25


def test_build_option_normalizes_call_put_alias():
    builder = make_builder()
    contract = builder.build_option("NIFTY", 22000, "2026-09-25", "CALL")
    assert contract.option_type == "CE"


def test_build_option_invalid_strike_step_raises():
    builder = make_builder()
    try:
        builder.build_option("NIFTY", 22025, "2026-09-25", "CE")  # step is 50
        assert False
    except ContractBuildError:
        pass


def test_build_option_non_optionable_underlying_raises():
    builder = make_builder()
    try:
        builder.build_option("GOLD", 60000, "2026-09-25", "CE")  # no strike_step
        assert False
    except ContractBuildError:
        pass


def test_build_option_unknown_underlying_raises():
    builder = make_builder()
    try:
        builder.build_option("GHOST", 100, "2026-09-25", "CE")
        assert False
    except ContractBuildError:
        pass


def test_build_option_bad_expiry_format_raises():
    builder = make_builder()
    try:
        builder.build_option("NIFTY", 22000, "25-09-2026", "CE")
        assert False
    except ContractBuildError:
        pass


def test_build_future_valid():
    builder = make_builder()
    contract = builder.build_future("GOLD", "2026-10-05")
    assert contract.underlying_symbol == "GOLD"
    assert contract.lot_size == 100


def test_build_future_no_expiry_cycle_raises():
    builder = make_builder()
    try:
        builder.build_future("AAPL", "2026-10-05")  # equity has no expiry cycle
        assert False
    except ContractBuildError:
        pass


def test_trading_symbol_format():
    builder = make_builder()
    contract = builder.build_option("NIFTY", 22000, "2026-09-25", "PE")
    assert contract.trading_symbol == "NIFTY2026092522000PE"
