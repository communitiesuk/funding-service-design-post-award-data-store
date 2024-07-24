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
from typing import Literal

import pandas as pd
import pandera as pa

from data_store.transformation.utils import POSTCODE_REGEX
from data_store.validation.pathfinders.schema_validation.consts import PFErrors, PFRegex


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


def is_datetime():
    def _is_datetime(element):
        try:
            pd.to_datetime(element)
            return True
        except ValueError:
            return False

    return pa.Check(_is_datetime, element_wise=True, error=PFErrors.IS_DATETIME)


def is_int():
    def _is_int(element):
        coerced = pd.to_numeric(element, errors="coerce")
        return pd.notnull(coerced) and (isinstance(coerced, float) or coerced.astype(float).is_integer())

    return pa.Check(_is_int, element_wise=True, error=PFErrors.IS_INT)


def is_float():
    def _is_float(element):
        coerced = pd.to_numeric(element, errors="coerce")
        return pd.notnull(coerced)

    return pa.Check(_is_float, element_wise=True, error=PFErrors.IS_FLOAT)


def not_in_future():
    """
    Checks that a datetime is not in the future.
    """

    def _not_in_future(element):
        if _should_fail_check_because_element_is_nan(element):
            return False

        # If it's not come through here as a datetime, it's probably some other native data type like an int or string,
        # which will fail datetime coercion later in the pipeline. We throw a TypeError here as these are ignored by
        # some custom logic we have, see tables.validate:TableValidator.IGNORED_FAILURES)
        if not isinstance(element, datetime):
            raise TypeError("Value must be a datetime")
        return element <= datetime.now().date()

    return pa.Check(_not_in_future, element_wise=True, error=PFErrors.FUTURE_DATE)


def max_word_count(max_words: int):
    """
    Checks that a string split up by whitespace characters is less than or equal to "max_words" elements long.
    """

    def _max_word_count(element):
        if _should_fail_check_because_element_is_nan(element):
            return False

        # If it's not come through here as a string, it's probably some other native data type like an int, float, or
        # datetime. Which won't be more than 100 words.
        if not isinstance(element, str):
            raise TypeError("Value must be a string")
        return len(element.split()) <= max_words

    return pa.Check(_max_word_count, element_wise=True, error=PFErrors.LTE_X_WORDS.format(x=max_words))


def postcode_list():
    """
    Checks that a string can be split on commas and each element matches a basic UK postcode regex.
    """

    def _postcode_list(element):
        if _should_fail_check_because_element_is_nan(element):
            return False

        # If we've been passed anything that's not a string (eg an int or datetime), we already know it's not going to
        # have a postcode format, so we can fail. We don't raise a TypeError here, because our table validation ignores
        # TypeErrors raised from these pandera checks, which would lead to not reporting the cell as an invalid
        # postcode.
        if not isinstance(element, str):
            return False

        postcodes = element.split(",")
        for postcode in postcodes:
            postcode = postcode.strip()
            if not re.match(POSTCODE_REGEX, postcode):
                return False
        return True

    return pa.Check(_postcode_list, element_wise=True, error=PFErrors.INVALID_POSTCODE_LIST)


def exactly_x_rows(x: int):
    """
    Checks that a dataframe has exactly x rows.
    """

    def _exactly_x_rows(df):
        return df.shape[0] == x

    return pa.Check(_exactly_x_rows, error=PFErrors.EXACTLY_X_ROWS.format(x=x))


def email_regex():
    return pa.Check.str_matches(PFRegex.BASIC_EMAIL, error=PFErrors.EMAIL)


def phone_regex():
    return pa.Check.str_matches(PFRegex.BASIC_TELEPHONE, error=PFErrors.PHONE_NUMBER)


def greater_than(x: int):
    return pa.Check.greater_than(x, error=PFErrors.GREATER_THAN.format(x=x))


def greater_than_or_equal_to(x: int):
    return pa.Check.greater_than_or_equal_to(x, error=PFErrors.GREATER_THAN_OR_EQUAL_TO.format(x=x))


def less_than(x: int):
    return pa.Check.less_than(x, error=PFErrors.LESS_THAN.format(x=x))


def is_in(allowed_values: list):
    def _is_in(element):
        return element in allowed_values

    return pa.Check(_is_in, element_wise=True, error=PFErrors.ISIN)
