from functools import partial

import pytest

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
