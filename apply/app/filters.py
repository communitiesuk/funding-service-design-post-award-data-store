from datetime import datetime

from app.models.statuses import get_formatted
from flask_babel import format_datetime
from flask_babel import gettext


def date_format_short_month(value: datetime, format="dd MMM yyyy"):
    return format_datetime(value, format)


def datetime_format_short_month(value: datetime) -> str:
    if value:
        formatted_date = format_datetime(value, format="dd MMM yyyy ")
        formatted_date += gettext("at")
        formatted_date += format_datetime(value, format=" h:mm", rebase=False)
        formatted_date += format_datetime(value, "a", rebase=False).lower()
        return formatted_date
    else:
        return ""


def custom_format_datetime(date_string, output_format="%d/%m/%Y"):
    original_date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%f")
    formatted_date = original_date.strftime(output_format)
    return formatted_date


def datetime_format(value: str) -> str:
    """
    Format a date-time string to match the GOV.UK style guide.

    This function takes a date-time string in the format "%Y-%m-%dT%H:%M:%S" and
    returns it in a human-readable format that adheres to the guidelines provided by
    the GOV.UK style guide.

    Specifically:
    - The time "00:00" is represented as "midnight".
    - The time "12:00" is represented as "midday".
    - All other times are in the format "HH:MMam/pm" without leading zeros in the hour.

    Parameters:
    - value (str): The date-time string to be formatted.
                   Example: "2020-01-01T12:00:00"

    Returns:
    - str: A string representing the date-time in the GOV.UK recommended style.

    Reference:
    - https://www.gov.uk/guidance/style-guide/a-to-z-of-gov-uk-style#times
    """
    parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")

    if parsed.time().hour == 0 and parsed.time().minute == 0:
        time_str = "midnight"
    elif parsed.time().hour == 12 and parsed.time().minute == 0:
        time_str = "midday"
    else:
        time_str = parsed.strftime("%I:%M%p").lstrip("0").lower()

    formatted_date = parsed.strftime("%d %B %Y ")
    formatted_date += gettext("at")
    formatted_date += " " + time_str
    return formatted_date


def snake_case_to_human(word: str) -> str | None:
    if word:
        return word.replace("_", " ").strip().title()


def kebab_case_to_human(word: str) -> str | None:
    """Should NOT be used to unslugify as '-' are
    also used to replace other special characters"""
    if word:
        return word.replace("-", " ").strip().capitalize()


def status_translation(value: str):
    if value:
        return get_formatted(value)


def string_to_datetime(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")


def datetime_format_full_month(value: datetime) -> str:
    if not value:
        return ""
    formatted_date = format_datetime(value, format="dd MMMM yyyy ")
    formatted_date += gettext("at")
    formatted_date += format_datetime(value, format=" h:mm", rebase=False)
    formatted_date += format_datetime(value, "a", rebase=False).lower()
    return formatted_date
