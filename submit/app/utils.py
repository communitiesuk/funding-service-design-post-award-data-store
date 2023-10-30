from datetime import datetime

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


def calculate_days_to_deadline(current_date=datetime.now().date()):
    """Calculate the number of days remaining until a specified submission deadline.
    The due_date is a str representation of submission deadline in format dd/mm/yyyy.
    It is set in main/config/envs/default.py

    :param current_date: datetime object representing today's date in format yyyy-mm-dd
    Returns:
    :int: The number of days remaining until the submission deadline.
    """

    due_date = Config.SUBMIT_DEADLINE
    delta = datetime.strptime(due_date, "%d/%m/%Y").date() - current_date
    return delta.days


def is_load_enabled():
    """Checks config to see if loading to the db is enabled.

    :return: True if loading submissions into the database is enabled, otherwise False
    """
    return True if not Config.DISABLE_LOAD else False
