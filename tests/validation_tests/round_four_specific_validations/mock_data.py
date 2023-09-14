import pandas as pd
import pytest


@pytest.fixture
def valid_review_and_sign_off_section():
    valid_review_and_sign_off_section = {
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

    return valid_review_and_sign_off_section


@pytest.fixture
def invalid_review_and_sign_off_section():
    invalid_review_and_sign_off_section = {
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

    return invalid_review_and_sign_off_section
