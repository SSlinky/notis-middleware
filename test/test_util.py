"""Tests for utility functions."""
from app.util import get_month_range
import datetime


def test_get_month_range():
    """Test the get_month_range function."""
    date = datetime.datetime(2024, 6, 15)
    first_day, last_day = get_month_range(date)
    assert first_day == datetime.datetime(2024, 6, 1)
    assert last_day == datetime.datetime(2024, 6, 30)


def test_get_month_range_december():
    """Test the get_month_range function for December."""
    date = datetime.datetime(2024, 12, 15)
    first_day, last_day = get_month_range(date)
    assert first_day == datetime.datetime(2024, 12, 1)
    assert last_day == datetime.datetime(2024, 12, 31)
