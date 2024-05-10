"""Module for custom Pandera Check methods."""

import math
import re
from datetime import datetime
from typing import Any, Literal

import pandas as pd
import pandera as pa

from core.transformation.utils import POSTCODE_REGEX
from core.validation.pathfinders.schema_validation.consts import PFErrors, PFRegex


def _should_fail_check_because_element_is_nan(element: Any) -> Literal[True] | None:
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


def datetime_check():
    def is_datetime(element: Any):
        try:
            pd.to_datetime(element)
            return True
        except ValueError:
            return False

    return pa.Check(is_datetime, element_wise=True, error=PFErrors.IS_DATETIME)


def int_check():
    def is_int(element: Any):
        coerced = pd.to_numeric(element, errors="coerce")
        return pd.notnull(coerced) and (isinstance(coerced, float) or coerced.astype(float).is_integer())

    return pa.Check(is_int, element_wise=True, error=PFErrors.IS_INT)


def float_check():
    def is_float(element: Any):
        coerced = pd.to_numeric(element, errors="coerce")
        return pd.notnull(coerced)

    return pa.Check(is_float, element_wise=True, error=PFErrors.IS_FLOAT)


def max_word_count_check(max_words: int):
    def max_word_count(element: Any):
        if _should_fail_check_because_element_is_nan(element):
            return False
        if not isinstance(element, str):
            raise TypeError("Value must be a string")
        return len(element.split()) <= max_words

    return pa.Check(max_word_count, element_wise=True, error=PFErrors.LTE_X_WORDS.format(max_words=max_words))


def not_in_future_check():
    def not_in_future(element: Any):
        if _should_fail_check_because_element_is_nan(element):
            return False
        if not isinstance(element, datetime):
            raise TypeError("Value must be a datetime")
        return element <= datetime.now().date()

    return pa.Check(not_in_future, element_wise=True, error=PFErrors.FUTURE_DATE)


def postcode_list_check():
    def postcode_list(element: Any):
        if _should_fail_check_because_element_is_nan(element):
            return False
        if not isinstance(element, str):
            return False
        postcodes = element.split(",")
        for postcode in postcodes:
            postcode = postcode.strip()
            if not re.match(POSTCODE_REGEX, postcode):
                return False
        return True

    return pa.Check(postcode_list, element_wise=True, error=PFErrors.INVALID_POSTCODE_LIST)


def exactly_x_rows_check(num_rows: int):
    def exactly_x_rows(df: pd.DataFrame):
        return df.shape[0] == num_rows

    return pa.Check(exactly_x_rows, error=PFErrors.EXACTLY_X_ROWS.format(num_rows=num_rows))


def email_regex_check():
    return pa.Check.str_matches(PFRegex.BASIC_EMAIL, error=PFErrors.EMAIL)


def phone_regex_check():
    return pa.Check.str_matches(PFRegex.BASIC_TELEPHONE, error=PFErrors.PHONE_NUMBER)


def greater_than_check(num: int):
    return pa.Check.greater_than(num, error=PFErrors.GREATER_THAN.format(num=num))


def greater_than_or_equal_to_check(num: int):
    return pa.Check.greater_than_or_equal_to(num, error=PFErrors.GREATER_THAN_OR_EQUAL_TO.format(num=num))


def less_than_check(num: int):
    return pa.Check.less_than(num, error=PFErrors.LESS_THAN.format(num=num))


def less_than_or_equal_to_check(num: int):
    return pa.Check.less_than_or_equal_to(num, error=PFErrors.LESS_THAN_OR_EQUAL_TO.format(num=num))


def is_in_check(allowed_values: list):
    def is_in(element: Any):
        return element in allowed_values

    return pa.Check(is_in, element_wise=True, error=PFErrors.ISIN)
