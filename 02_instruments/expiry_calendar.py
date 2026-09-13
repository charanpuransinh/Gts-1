"""
expiry_calendar.py
====================
MODULE   : 02_instruments
OWNER    : AI-2 (Instruments)
PURPOSE  : Computes option/future expiry dates for weekly and monthly
           cycles, and finds the "current" / "next" expiry relative to
           a given date. Holiday adjustment hook is provided but the
           actual exchange holiday list must be injected by the caller
           (kept out of this file so it isn't silently wrong/outdated).

INPUT    : reference date, ExpiryFrequency, optional holiday set
OUTPUT   : expiry date strings ("YYYY-MM-DD"), sorted expiry lists
CALLER   : contract_builder.py, 06_options_engine.*, 07_strategy.* (expiry
           specialist strategy needs "days to expiry")
CALLEE   : instrument_types
DEPENDS  : instrument_types, stdlib datetime
"""

from __future__ import annotations
from datetime import date, timedelta
from typing import List, Optional, Set

from instrument_types import ExpiryFrequency

# Monday=0 ... Sunday=6
WEEKDAY_TUESDAY = 1
WEEKDAY_THURSDAY = 3


def _next_weekday_on_or_after(d: date, target_weekday: int) -> date:
    delta = (target_weekday - d.weekday()) % 7
    return d + timedelta(days=delta)


def _last_weekday_of_month(year: int, month: int, target_weekday: int) -> date:
    if month == 12:
        first_of_next = date(year + 1, 1, 1)
    else:
        first_of_next = date(year, month + 1, 1)
    last_day = first_of_next - timedelta(days=1)
    delta = (last_day.weekday() - target_weekday) % 7
    return last_day - timedelta(days=delta)


def _adjust_for_holidays(d: date, holidays: Optional[Set[date]]) -> date:
    """If the computed expiry falls on a holiday, roll back one trading day."""
    if not holidays:
        return d
    while d in holidays or d.weekday() >= 5:  # also skip weekends defensively
        d -= timedelta(days=1)
    return d


def weekly_expiry_on_or_after(ref: date, weekday: int = WEEKDAY_THURSDAY,
                               holidays: Optional[Set[date]] = None) -> date:
    """
    Next weekly expiry on/after `ref`. NIFTY historically expires Thursday;
    pass a different `weekday` for instruments with a different cycle.
    """
    candidate = _next_weekday_on_or_after(ref, weekday)
    return _adjust_for_holidays(candidate, holidays)


def monthly_expiry_on_or_after(ref: date, weekday: int = WEEKDAY_THURSDAY,
                                holidays: Optional[Set[date]] = None) -> date:
    """Last `weekday` of the month containing `ref`, or next month's if already past."""
    candidate = _last_weekday_of_month(ref.year, ref.month, weekday)
    candidate = _adjust_for_holidays(candidate, holidays)
    if candidate < ref:
        next_month = ref.month + 1
        next_year = ref.year
        if next_month > 12:
            next_month = 1
            next_year += 1
        candidate = _last_weekday_of_month(next_year, next_month, weekday)
        candidate = _adjust_for_holidays(candidate, holidays)
    return candidate


def next_expiry(ref: date, frequency: ExpiryFrequency, weekday: int = WEEKDAY_THURSDAY,
                 holidays: Optional[Set[date]] = None) -> Optional[date]:
    if frequency == ExpiryFrequency.WEEKLY:
        return weekly_expiry_on_or_after(ref, weekday, holidays)
    if frequency == ExpiryFrequency.MONTHLY:
        return monthly_expiry_on_or_after(ref, weekday, holidays)
    return None


def expiry_series(ref: date, frequency: ExpiryFrequency, count: int,
                   weekday: int = WEEKDAY_THURSDAY,
                   holidays: Optional[Set[date]] = None) -> List[date]:
    """Returns the next `count` expiry dates on/after `ref`, ascending."""
    if count <= 0:
        return []
    result: List[date] = []
    cursor = ref
    if frequency == ExpiryFrequency.WEEKLY:
        while len(result) < count:
            e = weekly_expiry_on_or_after(cursor, weekday, holidays)
            result.append(e)
            cursor = e + timedelta(days=1)
    elif frequency == ExpiryFrequency.MONTHLY:
        while len(result) < count:
            e = monthly_expiry_on_or_after(cursor, weekday, holidays)
            result.append(e)
            cursor = e + timedelta(days=1)
    return result


def days_to_expiry(ref: date, expiry: date) -> int:
    return (expiry - ref).days
