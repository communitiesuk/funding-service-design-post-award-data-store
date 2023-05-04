import pytest

from core.util import postcode_to_itl1
from core.db import db


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


def test_postcode_to_itl1_invalid_postcode_raises_error():
    """Tests that the mapping function returns a custom ValueError message for an invalid postcode."""

    with pytest.raises(ValueError) as exc_info:
        postcode_to_itl1("NOT A POSTCODE")

    assert exc_info.value.args[0] == "Postcode is invalid."


def test_postcode_to_itl1_post_code_area_not_exist_raises_error():
    """Tests that the mapping function returns a custom KeyError message for a postcode with an invalid area code."""

    with pytest.raises(KeyError) as exc_info:
        postcode_to_itl1("ZZ1 2AB")

    assert exc_info.value.args[0] == 'Postcode Area "ZZ" is invalid and has no mapping.'


def seed_test_database(model, model_data):

    model_rows = []
    cols = len(next(iter(model_data.values())))
    for idx in range(cols):
        model_args = {
            key: val[idx] for key, val in model_data.items()
        }
        model_rows.append(
            model(
                **model_args
            )
        )

    db.session.add_all(model_rows)
