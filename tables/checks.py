"""Module for custom Check methods.

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
from datetime import datetime

import pandera as pa
import pandera.strategies as st
from hypothesis import strategies
from pandera import extensions


def word_count_less_than_strategy(pandera_dtype: pa.DataType, strategy: st.SearchStrategy | None = None, *, max_words):
    """A strategy for synthesising data that abides by the "word_count_less_than" Check constraint."""
    if strategy is None:
        return st.pandas_dtype_strategy(
            pandera_dtype,
            strategy=strategies.text().filter(lambda x: len(x.split()) < max_words),
        )
    return strategy.filter(lambda x: len(x.split()) < max_words)


@extensions.register_check_method(
    statistics=["max_words"], check_type="element_wise", strategy=word_count_less_than_strategy
)
def word_count_less_than(element, *, max_words):
    """Checks that a string split up by whitespace characters is less than or equal to "max_words" elements long.

    :param element: an element to check
    :param max_words: the maximum allowed length of the string split up by whitespace
    :return: True if passes the check, else False
    """
    if not isinstance(element, str):
        raise TypeError("Value must be a string")
    return len(element.split()) <= max_words


def not_in_future_strategy(pandera_dtype: pa.DataType, strategy: st.SearchStrategy | None = None):
    """A strategy for synthesising data that abides by the "not_in_future" Check constraint."""
    if strategy is None:
        return st.pandas_dtype_strategy(
            pandera_dtype,
            strategy=strategies.datetimes(max_value=datetime.now()),
        )
    return strategy.filter(lambda x: x <= datetime.now().date())


@extensions.register_check_method(statistics=[], check_type="element_wise", strategy=not_in_future_strategy)
def not_in_future(element):
    """Checks that a datetime is not in the future.

    :param element: an element to check
    :return: True if passes the check, else False
    """
    if not isinstance(element, datetime):
        raise TypeError("Value must be a datetime")
    return element <= datetime.now().date()
