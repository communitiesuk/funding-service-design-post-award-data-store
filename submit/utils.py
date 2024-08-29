from datetime import date

from config import Config


def days_between_dates(date1: date, date2: date) -> int:
    """Calculate the number of days between two dates.

    :param date1: a date object
    :param date2: another date object
    :return: The number of days between the two dates
    """
    delta = date2 - date1
    return delta.days


def is_load_enabled():
    """Checks config to see if loading to the db is enabled.

    :return: True if loading submissions into the database is enabled, otherwise False
    """
    return True if not Config.DISABLE_LOAD else False
