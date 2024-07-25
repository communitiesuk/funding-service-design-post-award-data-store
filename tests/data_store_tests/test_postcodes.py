import numpy as np

from data_store.transformation.utils import extract_postcodes
from data_store.util import get_postcode_prefix_set


def test_postcode_prefix_returns_prefix():
    itl1 = get_postcode_prefix_set(["DT1 8PD"])
    assert itl1 == {"DT"}


def test_postcode_prefix_returns_prefix_no_space_between():
    itl1 = get_postcode_prefix_set(["DT18PD"])
    assert itl1 == {"DT"}


def test_postcode_prefix_returns_prefix_only_first_half():
    itl1 = get_postcode_prefix_set(["DT1"])
    assert itl1 == {"DT"}


def test_postcode_prefix_returns_prefix_lowercase():
    itl1 = get_postcode_prefix_set(["dt1 8pd"])
    assert itl1 == {"DT"}


def test_postcode_prefix_returns_prefix_leading_space():
    itl1 = get_postcode_prefix_set([" DT1 8PD"])
    assert itl1 == {"DT"}


def test_postcode_prefix_returns_prefix_trailing_space():
    itl1 = get_postcode_prefix_set(["DT1 8PD "])
    assert itl1 == {"DT"}


def test_postcode_prefix_returns_prefix_single_letter_area():
    itl1 = get_postcode_prefix_set(["E1 8PD"])
    assert itl1 == {"E"}


def test_extract_postcodes_list_of_matches():
    postcode_string = (
        "1. Pedestrian Gateway \nBN9 0DF (Nr Station); \n2. Wayfinding\nBN9 9BP (Riverside); \nBN9 9BN "
        "(Denton Island); \nBN9 9QD (Huggetts Green); \nBN9 0AS (Near railway station); \nBN9 9PA "
        "(Near jobcentre); \nBN9 9PD (High St path leading to North Lane bus stop); \nBN9 0DF (Ferry "
        "car passenger signage)"
    )

    postcodes = extract_postcodes(postcode_string)

    assert postcodes == ["BN9 0DF", "BN9 9BP", "BN9 9BN", "BN9 9QD", "BN9 0AS", "BN9 9PA", "BN9 9PD", "BN9 0DF"]


def test_extract_postcodes_list_of_matches_prepended_and_appended_chars():
    """Tests that those postcodes are not returned where there are additional characters before or after a
    valid postcode (except for new line characters before that).  e.g. shouldn't return BN9 0DFA, because
    the 'A' makes the valid postcode invalid"""
    postcode_string = (
        "1. Pedestrian Gateway \nBN9 0DFA (Nr Station); \n2. Wayfinding\n\nBN9 9BP (Riverside); \nBBN9 9BN "
        "(Denton Island); \nBN9 9QD\n (Huggetts Green); \nBN9 0AS (Near railway station); \nBN9 9PA "
        "(Near jobcentre); \nBN9 9PDd (High St path leading to North Lane bus stop); \nBN9 0DF3 (Ferry "
        "car passenger signage)"
    )

    postcodes = extract_postcodes(postcode_string)

    assert postcodes == ["BN9 9BP", "BN9 9QD", "BN9 0AS", "BN9 9PA"]


def test_extract_postcodes_no_matches_returns_single_item_list():
    postcode_string = "BN9 0DF"

    postcodes = extract_postcodes(postcode_string)

    assert postcodes == ["BN9 0DF"]


def test_extract_postcodes_no_matches_returns_empty_list():
    postcode_string = ""

    postcodes = extract_postcodes(postcode_string)

    assert postcodes is None


def test_extract_postcodes_no_matches_nan_returns_empty_list():
    postcode_string = np.nan

    postcodes = extract_postcodes(postcode_string)

    assert postcodes is None
