"""
test_expiry_calendar.py
MODULE: 02_instruments (tests)
OWNER : AI-2
"""

import sys, os
from datetime import date
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from expiry_calendar import (
    weekly_expiry_on_or_after, monthly_expiry_on_or_after, expiry_series,
    days_to_expiry, WEEKDAY_THURSDAY,
)
from instrument_types import ExpiryFrequency


def test_weekly_expiry_lands_on_thursday():
    ref = date(2026, 9, 15)  # a Tuesday
    expiry = weekly_expiry_on_or_after(ref)
    assert expiry.weekday() == WEEKDAY_THURSDAY
    assert expiry >= ref


def test_weekly_expiry_when_ref_is_the_expiry_day():
    ref = date(2026, 9, 17)  # a Thursday
    expiry = weekly_expiry_on_or_after(ref)
    assert expiry == ref


def test_monthly_expiry_is_last_thursday_of_month():
    ref = date(2026, 9, 1)
    expiry = monthly_expiry_on_or_after(ref)
    assert expiry.month == 9
    assert expiry.weekday() == WEEKDAY_THURSDAY
    # no later Thursday in the same month
    from datetime import timedelta
    assert (expiry + timedelta(days=7)).month != 9


def test_monthly_expiry_rolls_to_next_month_if_past():
    ref = date(2026, 9, 30)  # after this month's expiry
    expiry = monthly_expiry_on_or_after(ref)
    assert expiry.month == 10


def test_holiday_adjustment_rolls_back():
    ref = date(2026, 9, 15)
    expiry_no_holiday = weekly_expiry_on_or_after(ref)
    holidays = {expiry_no_holiday}
    expiry_with_holiday = weekly_expiry_on_or_after(ref, holidays=holidays)
    assert expiry_with_holiday < expiry_no_holiday


def test_expiry_series_ascending_and_correct_count():
    ref = date(2026, 9, 1)
    series = expiry_series(ref, ExpiryFrequency.WEEKLY, count=4)
    assert len(series) == 4
    assert series == sorted(series)
    assert len(set(series)) == 4  # all distinct


def test_days_to_expiry():
    assert days_to_expiry(date(2026, 9, 1), date(2026, 9, 11)) == 10
