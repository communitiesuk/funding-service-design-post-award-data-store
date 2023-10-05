from datetime import datetime

from config import Config


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
