from datetime import date

from flask import current_app

from app.const import FUND_TYPE_ID_TO_FRIENDLY_NAME
from config import Config


def get_friendly_fund_type(fund_type_id: str) -> str | None:
    """Gets a friendly fund type name from an ID.

    If fund_type_id is not recognised, it is logged and None is returned.

    :param fund_type_id: fund type ID
    :return: friendly fund type name
    """
    try:
        return FUND_TYPE_ID_TO_FRIENDLY_NAME[fund_type_id]
    except KeyError:
        current_app.logger.error(f"Unknown fund type id found: {fund_type_id}")


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
