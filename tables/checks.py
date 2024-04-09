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

import math
import re
from datetime import datetime
from typing import Any, Literal

import pandas as pd
import pandera as pa
from pandera.extensions import CheckType

from core.transformation.utils import POSTCODE_REGEX


def _should_fail_check_because_element_is_nan(element) -> Literal[True] | None:
    """Detect nan values in pandera checks which should return false to bypass type errors.

    When writing element-wise pandera checks, pandera will pass through any null/nan values rather than skipping over
    them. These are represented as `float('nan')` values. Many of our checks validate the type of the element,
    expecting a specific thing - eg a datetime or string. The null/na values will fail those checks. We raise TypeErrors
    if the data type doesn't match what we expect, but explicitly ignore TypeErrors raised from these checks because we
    expect a later part of our pipeline to catch and report data coercion errors (coerce.controllers.ingest:coerce_data)

    If we instead mark null/na values as failing these checks, panderas has logic to automatically disregard the rows
    failing for this reason from the specific check taking place. So if, for example, a null value is passed into a
    postcode validation function, we can safely fail that check without worrying about the cell being reported for an
    invalid formatted postcode. It will only be reported as an empty cell missing data error instead.
    """
    if isinstance(element, float) and math.isnan(element):
        return True

    return None


@pa.extensions.register_check_method(check_type=CheckType.ELEMENT_WISE)
def is_datetime(element):
    try:
        pd.to_datetime(element)
        return True
    except ValueError:
        return False


@pa.extensions.register_check_method(check_type=CheckType.ELEMENT_WISE)
def is_int(element):
    coerced = pd.to_numeric(element, errors="coerce")
    return pd.notnull(coerced) and (isinstance(coerced, float) or coerced.astype(float).is_integer())


@pa.extensions.register_check_method(check_type=CheckType.ELEMENT_WISE)
def is_float(element):
    coerced = pd.to_numeric(element, errors="coerce")
    return pd.notnull(coerced)


@pa.extensions.register_check_method(check_type=CheckType.ELEMENT_WISE)
def not_in_future(element: Any):
    """Checks that a datetime is not in the future.

    :param element: an element to check
    :return: True if passes the check, else False
    """
    if _should_fail_check_because_element_is_nan(element):
        return False

    if not isinstance(element, datetime):
        raise TypeError("Value must be a datetime")
    return element <= datetime.now().date()


@pa.extensions.register_check_method(statistics=["max_words"], check_type=CheckType.ELEMENT_WISE)
def max_word_count(element: Any, *, max_words):
    """Checks that a string split up by whitespace characters is less than or equal to "max_words" elements long.

    :param element: an element to check
    :param max_words: the maximum allowed length of the string split up by whitespace
    :return: True if passes the check, else False
    """
    if _should_fail_check_because_element_is_nan(element):
        return False
    if not isinstance(element, str):
        raise TypeError("Value must be a string")
    return len(element.split()) <= max_words


@pa.extensions.register_check_method(check_type=CheckType.ELEMENT_WISE)
def postcode_list(element: Any):
    """Checks that a string can be split on commas and each element matches a basic UK postcode regex.

    :param element: an element to check
    :return: True if passes the check, else False
    """
    if _should_fail_check_because_element_is_nan(element):
        return False
    if not isinstance(element, str):
        raise TypeError("Value must be a string")
    postcodes = element.split(",")
    for postcode in postcodes:
        postcode = postcode.strip()
        if not re.match(POSTCODE_REGEX, postcode):
            return False
    return True


@pa.extensions.register_check_method(check_type=CheckType.VECTORIZED)
def exactly_five_rows(df):
    return df.shape[0] == 5
