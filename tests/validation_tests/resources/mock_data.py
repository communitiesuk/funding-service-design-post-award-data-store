import pandas as pd
import pytest

from core.const import TF_PLACE_NAMES_TO_ORGANISATIONS


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
                0: ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
                1: [
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "Name",
                    "Role",
                    "Signature",
                    "Date",
                    "",
                    "",
                    "",
                    "Name",
                    "Role",
                    "Signature",
                    "Date",
                    "",
                ],
                2: [
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "John",
                    "Head of Tree Planting",
                    "Image1",
                    "01/01/2260",
                    "",
                    "",
                    "",
                    "John",
                    "Head of Tree Planting",
                    "Image2",
                    "01/01/2260",
                    "",
                ],
            }
        ),
    }
    return valid_workbook


@pytest.fixture
def valid_workbook_round_four():
    valid_workbook_round_four = {
        "1 - Start Here": pd.DataFrame(
            {
                0: ["", "", "", "", "", "", "", "", ""],
                1: [
                    "",
                    "",
                    "",
                    "",
                    "1 April 2023 to 30 September 2023",
                    "",
                    "Town Deals and Future High Streets Fund Reporting Template (v4.3)",
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
                0: ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
                1: [
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "Name",
                    "Role",
                    "Signature",
                    "Date",
                    "",
                    "",
                    "",
                    "Name",
                    "Role",
                    "Signature",
                    "Date",
                    "",
                ],
                2: [
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "John",
                    "Head of Tree Planting",
                    "Image1",
                    "01/01/2260",
                    "",
                    "",
                    "",
                    "John",
                    "Head of Tree Planting",
                    "Image2",
                    "01/01/2260",
                    "",
                ],
            }
        ),
    }
    return valid_workbook_round_four


@pytest.fixture
def invalid_workbook_round_four():
    invalid_workbook_round_four = {
        "1 - Start Here": pd.DataFrame(
            {
                0: ["", "", "", "", "", "", "", "", ""],
                1: [
                    "",
                    "",
                    "",
                    "",
                    "1 April 2023 to 30 September 2023",
                    "",
                    "Town Deals and Future High Streets Fund Reporting Template (v4.0)",
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
                0: ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
                1: [
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "Name",
                    "Role",
                    "Signature",
                    "Date",
                    "",
                    "",
                    "",
                    "Name",
                    "Role",
                    "Signature",
                    "Date",
                    "",
                ],
                2: [
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "Head of Tree Planting",
                    "Image1",
                    "01/01/2260",
                    "",
                    "",
                    "",
                    "John",
                    "",
                    "Image2",
                    "",
                    "",
                ],
            }
        ),
    }
    return invalid_workbook_round_four


@pytest.fixture
def valid_submission_details():
    return {
        "Fund Type": ("Town_Deal", {"Town_Deal", "Future_High_Street_Fund"}),
        "Form Version": (
            "Town Deals and Future High Streets Fund Reporting Template (v3.0)",
            {"Town Deals and Future High Streets Fund Reporting Template (v3.0)"},
        ),
        "Reporting Period": ("1 October 2022 to 31 March 2023", {"1 October 2022 to 31 March 2023"}),
        "Place Name": ("Newark", set(TF_PLACE_NAMES_TO_ORGANISATIONS.keys())),
    }
