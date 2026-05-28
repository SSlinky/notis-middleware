"""Basic utility functions."""
import datetime


def get_month_range(date: datetime.datetime):
    """Get the first and last day of the month for a given date.

    Args:
        date (datetime): The input date.
    """
    first_day = date.replace(day=1)
    if date.month == 12:
        last_day = date.replace(year=date.year + 1, month=1, day=1) \
            - datetime.timedelta(days=1)
    else:
        last_day = date.replace(month=date.month + 1, day=1) \
            - datetime.timedelta(days=1)
    return first_day, last_day
