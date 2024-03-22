"""Module for custom Check methods.

NOTE: using hypothesis to synthesize dataframes from Pandera schemas is extremely slow.

From pandera docs https://pandera.readthedocs.io/en/stable/extensions.html#extensions

One of the strengths of pandera is its flexibility in enabling you to define in-line custom checks on the fly:

>>> import pandera as pa
>>> # checks elements in a column/dataframe
>>> element_wise_check = pa.Check(lambda x: x < 0, element_wise=True)
>>> # applies the check function to a dataframe/series
>>> vectorized_check = pa.Check(lambda series_or_df: series_or_df < 0)

However, there are two main disadvantages of schemas with inline custom checks:
    1. they are not serializable with the IO interface.
    2. you can’t use them to synthesize data because the checks are not associated with a hypothesis strategy.
"""

import re
from datetime import datetime

import pandas as pd
import pandera as pa

from core.transformation.pathfinders.consts import PF_REPORTING_PERIOD_TO_DATES_2
from core.transformation.utils import POSTCODE_REGEX


@pa.extensions.register_check_method(check_type="element_wise")
def is_datetime(element):
    try:
        pd.to_datetime(element)
        return True
    except ValueError:
        return False


@pa.extensions.register_check_method(check_type="element_wise")
def is_int(element):
    coerced = pd.to_numeric(element, errors="coerce")
    return pd.notnull(coerced) and (isinstance(coerced, float) or coerced.astype(float).is_integer())


@pa.extensions.register_check_method(check_type="element_wise")
def is_float(element):
    coerced = pd.to_numeric(element, errors="coerce")
    return pd.notnull(coerced)


@pa.extensions.register_check_method(check_type="element_wise")
def not_in_future(element):
    """Checks that a datetime is not in the future.

    :param element: an element to check
    :return: True if passes the check, else False
    """
    if not isinstance(element, datetime):
        raise TypeError("Value must be a datetime")
    return element <= datetime.now().date()


@pa.extensions.register_check_method(statistics=["max_words"], check_type="element_wise")
def max_word_count(element, *, max_words):
    """Checks that a string split up by whitespace characters is less than or equal to "max_words" elements long.

    :param element: an element to check
    :param max_words: the maximum allowed length of the string split up by whitespace
    :return: True if passes the check, else False
    """
    if not isinstance(element, str):
        raise TypeError("Value must be a string")
    return len(element.split()) <= max_words


@pa.extensions.register_check_method(check_type="element_wise")
def postcode_list(element):
    """Checks that a string can be split on commas and each element matches a basic UK postcode regex.

    :param element: an element to check
    :return: True if passes the check, else False
    """
    if not isinstance(element, str):
        raise TypeError("Value must be a string")
    postcodes = element.split(",")
    for postcode in postcodes:
        postcode = postcode.strip()
        if not re.match(POSTCODE_REGEX, postcode):
            return False
    return True


@pa.extensions.register_check_method(check_type="vectorized")
def actual_forecast_matches_reporting_period(df: pd.DataFrame):
    """Checks that the value for "Actual, forecast or cancelled" matches the value for "Reporting period change takes
    place". If "Actual", then the reporting period start date should be in the past. If "Forecast", then the reporting
    period start date should be in the future. If "Cancelled", then any reporting period is valid.

    :param df: a dataframe to check
    :return: True if passes the check, else False
    """
    for _, row in df.iterrows():
        period = row["Reporting period change takes place"]
        reporting_period_ends_in_future = PF_REPORTING_PERIOD_TO_DATES_2[period]["end"].date() >= datetime.now().date()
        match row["Actual, forecast or cancelled"]:
            case "Actual":
                if reporting_period_ends_in_future:
                    return False
            case "Forecast":
                if not reporting_period_ends_in_future:
                    return False
            case "Cancelled":
                continue
    return True
