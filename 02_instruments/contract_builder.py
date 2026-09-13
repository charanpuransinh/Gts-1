"""
contract_builder.py
=====================
MODULE   : 02_instruments
OWNER    : AI-2 (Instruments)
PURPOSE  : Builds a fully-specified OptionContractSpec / FutureContractSpec
           from an underlying Instrument + strike + expiry, validating
           that the strike is on the instrument's strike step and the
           expiry matches its expiry_frequency. This is the only place
           that should construct tradable contract objects, so a bad
           strike/expiry combination is caught before it reaches
           execution.

INPUT    : InstrumentMaster, underlying symbol, strike, expiry date
OUTPUT   : OptionContractSpec / FutureContractSpec
CALLER   : 06_options_engine.*, 07_strategy.* (expiry specialist),
           14_execution.order_manager (symbol resolution)
CALLEE   : instrument_types, instrument_master, expiry_calendar
DEPENDS  : instrument_types, instrument_master, expiry_calendar
"""

from __future__ import annotations
from datetime import date
from typing import Optional

from instrument_types import (
    Instrument, OptionContractSpec, FutureContractSpec, SegmentType,
    ExpiryFrequency,
)
from instrument_master import InstrumentMaster, InstrumentNotFoundError


class ContractBuildError(ValueError):
    pass


class ContractBuilder:
    def __init__(self, master: InstrumentMaster):
        self.master = master

    def _get_optionable(self, underlying_symbol: str) -> Instrument:
        try:
            inst = self.master.get(underlying_symbol)
        except InstrumentNotFoundError as e:
            raise ContractBuildError(str(e)) from e
        if inst.strike_step is None:
            raise ContractBuildError(
                f"{underlying_symbol} has no strike_step; cannot build option contract"
            )
        return inst

    def build_option(self, underlying_symbol: str, strike: float,
                      expiry: str, option_type: str) -> OptionContractSpec:
        inst = self._get_optionable(underlying_symbol)

        option_type = option_type.upper()
        if option_type in ("C", "CALL"):
            option_type = "CE"
        elif option_type in ("P", "PUT"):
            option_type = "PE"
        if option_type not in ("CE", "PE"):
            raise ContractBuildError(f"invalid option_type: {option_type}")

        if strike <= 0:
            raise ContractBuildError(f"strike must be positive, got {strike}")
        remainder = round(strike % inst.strike_step, 6)
        if remainder not in (0, round(inst.strike_step, 6)):
            raise ContractBuildError(
                f"strike {strike} is not a multiple of strike_step "
                f"{inst.strike_step} for {underlying_symbol}"
            )

        self._validate_expiry_string(expiry)

        return OptionContractSpec(
            underlying_symbol=underlying_symbol,
            exchange=inst.exchange,
            strike=strike,
            expiry=expiry,
            option_type=option_type,
            lot_size=inst.lot_size,
            tick_size=inst.tick_size,
        )

    def build_future(self, underlying_symbol: str, expiry: str) -> FutureContractSpec:
        try:
            inst = self.master.get(underlying_symbol)
        except InstrumentNotFoundError as e:
            raise ContractBuildError(str(e)) from e

        if inst.expiry_frequency == ExpiryFrequency.NONE:
            raise ContractBuildError(
                f"{underlying_symbol} has no expiry cycle; cannot build future contract"
            )
        self._validate_expiry_string(expiry)

        return FutureContractSpec(
            underlying_symbol=underlying_symbol,
            exchange=inst.exchange,
            expiry=expiry,
            lot_size=inst.lot_size,
            tick_size=inst.tick_size,
        )

    @staticmethod
    def _validate_expiry_string(expiry: str) -> None:
        try:
            year, month, day = (int(x) for x in expiry.split("-"))
            date(year, month, day)
        except (ValueError, AttributeError) as e:
            raise ContractBuildError(
                f"expiry must be 'YYYY-MM-DD', got: {expiry!r}"
            ) from e
