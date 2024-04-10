import re

from functools import partial

import pytest

from core.table_configs.pathfinders.round_1 import PFRegex
from tables.checks import postcode_list
from tables.checks import max_word_count, not_in_future, postcode_list


@pytest.mark.parametrize(
    "postcode",
    [
        "SW1A1AA",
        "SW1A 1AA",
        "M11AE",
        "M1 1AE",
        "CR26XH",
        "CR2 6XH",
        "DN551PT",
        "DN55 1PT",
        "W1A1HQ",
        "W1A 1HQ",
        "EC1A1BB",
        "EC1A 1BB",
    ],
)
def test_postcode_list_valid_postcodes(postcode):
    assert postcode_list(postcode)


def test_postcode_list_valid_postcode_list():
    assert postcode_list("SW1A1AA, EC1A 1BB, M1 1AE")


@pytest.mark.parametrize("postcode", ["SW1A 1", "sw1a 1aa", "SW!A 1AA", "InvalidPostcode"])
def test_postcode_list_invalid_postcodes(postcode):
    assert not postcode_list(postcode)


def test_postcode_list_invalid_postcode_list():
    assert not postcode_list("SW1A1AA, InvalidPostcode, M1 1AE")


def test_postcode_list_empty_input():
    assert not postcode_list("")


@pytest.mark.parametrize("invalid_input", [123, ["SW1A1AA", "EC1A 1BB"]])
def test_postcode_list_non_string_input(invalid_input):
    assert postcode_list(invalid_input) is False


@pytest.mark.parametrize("partial_func", [not_in_future, partial(max_word_count, max_words=100), postcode_list])
def test_checks_return_false_on_nan(partial_func):
    assert partial_func(float("nan")) is False


@pytest.mark.parametrize(
    "number",
    [
        "01709 382121",
        "01204 333333",
        "0870 218 3829",
        "+44 1709 382121",
        "+441709382121",
    ],
)
def test_is_phone_number(number):
    assert re.match(PFRegex.BASIC_TELEPHONE, number)


@pytest.mark.parametrize(
    "number",
    [
        "paul",
        "01/02/25",
        "hello my name is paul",
        "1923612897361287361283761238761283716231827361",
        "0",
    ],
)
def test_is_not_phone_number(number):
    assert not re.match(PFRegex.BASIC_TELEPHONE, number)
