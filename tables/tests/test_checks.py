from datetime import datetime
from unittest.mock import patch

import pandas as pd
import pytest

from tables.checks import actual_forecast_matches_reporting_period, postcode_list


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
    with pytest.raises(TypeError) as excinfo:
        postcode_list(invalid_input)
    assert str(excinfo.value) == "Value must be a string"


@pytest.mark.parametrize(
    "actual_forecast_cancelled, reporting_period, expected_result",
    [
        ("Actual", "Q4 2023/24: Jan 2024 - Mar 2024", True),
        ("Actual", "Q1 2024/25: Apr 2024 - Jun 2024", False),
        ("Forecast", "Q4 2023/24: Jan 2024 - Mar 2024", False),
        ("Forecast", "Q1 2024/25: Apr 2024 - Jun 2024", True),
        ("Cancelled", "Q4 2023/24: Jan 2024 - Mar 2024", True),
    ],
)
def test_actual_forecast_matches_reporting_period(actual_forecast_cancelled, reporting_period, expected_result):
    with patch("tables.checks.datetime") as mock_datetime:
        mock_datetime.now.return_value = datetime(2024, 6, 1)
        df = pd.DataFrame(
            {
                "Actual, forecast or cancelled": [actual_forecast_cancelled],
                "Reporting period change takes place": [reporting_period],
            }
        )
        assert actual_forecast_matches_reporting_period(df) == expected_result
