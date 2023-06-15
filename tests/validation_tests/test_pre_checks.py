import pandas as pd
import pytest

import core.validation.failures as vf

# isort: off
from core.validation.initial_check import (
    extract_round_three_submission_details,
    pre_transformation_check,
)


@pytest.fixture
def valid_workbook():
    valid_workbook = {
        "1 - Start Here": pd.DataFrame(
            {
                0: ["", "", "", "", "", "", "", "", ""],
                1: [
                    "",
                    "",
                    "",
                    "",
                    "1 October 2022 to 31 March 2023",
                    "",
                    "Town Deals and Future High Streets Fund Reporting Template (v3.0)",
                    "",
                    "",
                ],
            }
        ),
        "2 - Project Admin": pd.DataFrame(
            {
                0: ["", "", "", "", "", "", "", "", ""],
                1: ["", "", "", "", "", "", "", "", ""],
                2: [
                    "",
                    "",
                    "",
                    "",
                    "",
                    "Are you filling this in for a Town Deal or Future High Street Fund?",
                    "Please select your place name",
                    "",
                    "",
                ],
                3: ["", "", "", "", "", "", "", "", ""],
                4: ["", "", "", "", "", "Town_Deal", "Newark", "", ""],
            }
        ),
        "3 - Programme Progress": pd.DataFrame(
            {
                0: ["test", "", "", "", "", "", "", "", ""],
                1: ["", "", "", "", "", "", "", "", ""],
                2: ["", "", "", "", "", "", "", "", ""],
                3: ["", "", "", "", "", "", "", "", ""],
                4: ["", "", "", "", "", "", "", "", ""],
            }
        ),
        "4a - Funding Profiles": pd.DataFrame(
            {
                0: ["test", "", "", "", "", "", "", "", ""],
                1: ["", "", "", "", "", "", "", "", ""],
                2: ["", "", "", "", "", "", "", "", ""],
                3: ["", "", "", "", "", "", "", "", ""],
                4: ["", "", "", "", "", "", "", "", ""],
            }
        ),
        "4b - PSI": pd.DataFrame(
            {
                0: ["test", "", "", "", "", "", "", "", ""],
                1: ["", "", "", "", "", "", "", "", ""],
                2: ["", "", "", "", "", "", "", "", ""],
                3: ["", "", "", "", "", "", "", "", ""],
                4: ["", "", "", "", "", "", "", "", ""],
            }
        ),
        "5 - Project Outputs": pd.DataFrame(
            {
                0: ["test", "", "", "", "", "", "", "", ""],
                1: ["", "", "", "", "", "", "", "", ""],
                2: ["", "", "", "", "", "", "", "", ""],
                3: ["", "", "", "", "", "", "", "", ""],
                4: ["", "", "", "", "", "", "", "", ""],
            }
        ),
        "6 - Outcomes": pd.DataFrame(
            {
                0: ["test", "", "", "", "", "", "", "", ""],
                1: ["", "", "", "", "", "", "", "", ""],
                2: ["", "", "", "", "", "", "", "", ""],
                3: ["", "", "", "", "", "", "", "", ""],
                4: ["", "", "", "", "", "", "", "", ""],
            }
        ),
        "7 - Risk Register": pd.DataFrame(
            {
                0: ["test", "", "", "", "", "", "", "", ""],
                1: ["", "", "", "", "", "", "", "", ""],
                2: ["", "", "", "", "", "", "", "", ""],
                3: ["", "", "", "", "", "", "", "", ""],
                4: ["", "", "", "", "", "", "", "", ""],
            }
        ),
        "8 - Review & Sign-Off": pd.DataFrame(
            {
                0: ["test", "", "", "", "", "", "", "", ""],
                1: ["", "", "", "", "", "", "", "", ""],
                2: ["", "", "", "", "", "", "", "", ""],
                3: ["", "", "", "", "", "", "", "", ""],
                4: ["", "", "", "", "", "", "", "", ""],
            }
        ),
    }
    return valid_workbook


@pytest.fixture
def valid_submission_details():
    return {
        "NullChecks": {
            "Place Name": "Newark",
        },
        "ValueChecks": {
            "Fund Type": ("Town_Deal", {"Town_Deal", "Future_High_Street_Fund"}),
            "Form Version": (
                "Town Deals and Future High Streets Fund Reporting Template (v3.0)",
                {"Town Deals and Future High Streets Fund Reporting Template (v3.0)"},
            ),
            "Reporting Period": ("1 October 2022 to 31 March 2023", {"1 October 2022 to 31 March 2023"}),
        },
    }


def test_extract_round_three_submission_details(valid_workbook):
    details_dict = extract_round_three_submission_details(valid_workbook)

    assert "Missing Sheets" not in details_dict
    assert details_dict["ValueChecks"]["Form Version"] == (
        "Town Deals and Future High Streets Fund Reporting Template (v3.0)",
        {"Town Deals and Future High Streets Fund Reporting Template (v3.0)"},
    )
    assert details_dict["ValueChecks"]["Reporting Period"] == (
        "1 October 2022 to 31 March 2023",
        {"1 October 2022 to 31 March 2023"},
    )
    assert details_dict["ValueChecks"]["Fund Type"] == (
        "Town_Deal",
        {"Town_Deal", "Future_High_Street_Fund"},
    )
    assert details_dict["NullChecks"]["Place Name"] == "Newark"


def test_pre_transformation_check_success(valid_submission_details):
    failures = pre_transformation_check(valid_submission_details)

    assert len(failures) == 0


def test_pre_transformation_check_failures(valid_submission_details):
    valid_submission_details["ValueChecks"]["Form Version"] = (
        "Invalid Form Version",
        {"Town Deals and Future High Streets Fund Reporting Template (v3.0)"},
    )
    failures = pre_transformation_check(valid_submission_details)

    assert len(failures) == 1
    assert isinstance(failures[0], vf.PreTransformationFailure)

    valid_submission_details["ValueChecks"]["Reporting Period"] = (
        "Invalid Reporting Period",
        {"1 October 2022 to 31 March 2023"},
    )
    failures = pre_transformation_check(valid_submission_details)
    assert len(failures) == 2
    assert isinstance(failures[1], vf.PreTransformationFailure)

    valid_submission_details["ValueChecks"]["Fund Type"] = (
        "Invalid Fund Type",
        {"Town_Deal", "Future_High_Street_Fund"},
    )
    failures = pre_transformation_check(valid_submission_details)
    assert len(failures) == 3
    assert isinstance(failures[2], vf.PreTransformationFailure)

    valid_submission_details["NullChecks"]["Place Name"] = ""
    failures = pre_transformation_check(valid_submission_details)
    assert len(failures) == 4
    assert isinstance(failures[3], vf.NoInputFailure)

    valid_submission_details["Invalid Sheets"] = ["1 - Start Here"]
    failures = pre_transformation_check(valid_submission_details)
    assert len(failures) == 1
    assert isinstance(failures[0], vf.InvalidSheetFailure)

    valid_submission_details["Missing Sheets"] = ["1 - Start Here"]
    failures = pre_transformation_check(valid_submission_details)
    assert len(failures) == 1
    assert isinstance(failures[0], vf.EmptySheetFailure)
