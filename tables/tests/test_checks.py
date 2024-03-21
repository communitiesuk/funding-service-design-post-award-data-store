import pytest

from tables.checks import postcode_list


def test_postcode_list_valid_postcodes():
    valid_postcodes = [
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
    ]
    for postcode in valid_postcodes:
        assert postcode_list(postcode)
    assert postcode_list("SW1A1AA, EC1A 1BB, M1 1AE")


def test_postcode_list_invalid_postcodes():
    invalid_postcodes = [
        "SW1A 1AA1",
        "SW1A 1",
        "sw1a 1aa",
        "SW!A 1AA",
        "InvalidPostcode",
    ]
    for postcode in invalid_postcodes:
        assert not postcode_list(postcode)
    assert not postcode_list("SW1A1AA, InvalidPostcode, M1 1AE")


def test_postcode_list_empty_input():
    assert not postcode_list("")


def test_postcode_list_non_string_input():
    with pytest.raises(TypeError):
        postcode_list(123)

    with pytest.raises(TypeError):
        postcode_list(["SW1A1AA", "EC1A 1BB"])
