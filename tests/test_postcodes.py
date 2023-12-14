import numpy as np

from core.extraction.utils import extract_postcodes
from core.util import postcode_to_itl1


def test_postcode_to_itl1_returns_itl1():
    itl1 = postcode_to_itl1("DT1 8PD")
    assert itl1 == "TLK"


def test_postcode_to_itl1_returns_itl1_no_space_between():
    itl1 = postcode_to_itl1("DT18PD")
    assert itl1 == "TLK"


def test_postcode_to_itl1_returns_itl1_only_first_half():
    itl1 = postcode_to_itl1("DT1")
    assert itl1 == "TLK"


def test_postcode_to_itl1_returns_itl1_lowercase():
    itl1 = postcode_to_itl1("dt1 8pd")
    assert itl1 == "TLK"


def test_postcode_to_itl1_returns_itl1_leading_space():
    itl1 = postcode_to_itl1(" DT1 8PD")
    assert itl1 == "TLK"


def test_postcode_to_itl1_returns_itl1_trailing_space():
    itl1 = postcode_to_itl1("DT1 8PD ")
    assert itl1 == "TLK"


def test_postcode_to_itl1_returns_itl1_single_letter_area():
    itl1 = postcode_to_itl1("E1 8PD")
    assert itl1 == "TLI"


def test_postcode_to_itl1_invalid_postcode_returns_none():
    """Tests that the mapping function returns None type for an invalid postcode."""
    assert postcode_to_itl1("NOT A POSTCODE") is None
    assert postcode_to_itl1("ZZ1 2AB") is None


def test_extract_postcodes_list_of_matches():
    postcode_string = (
        "1. Pedestrian Gateway \nBN9 0DF (Nr Station); \n2. Wayfinding\nBN9 9BP (Riverside); \nBN9 9BN "
        "(Denton Island); \nBN9 9QD (Huggetts Green); \nBN9 0AS (Near railway station); \nBN9 9PA "
        "(Near jobcentre); \nBN9 9PD (High St path leading to North Lane bus stop); \nBN9 0DF (Ferry "
        "car passenger signage)"
    )

    postcodes = extract_postcodes(postcode_string)

    assert postcodes == ["BN9 0DF", "BN9 9BP", "BN9 9BN", "BN9 9QD", "BN9 0AS", "BN9 9PA", "BN9 9PD", "BN9 0DF"]


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
