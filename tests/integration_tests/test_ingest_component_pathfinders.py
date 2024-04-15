import json
from pathlib import Path
from typing import BinaryIO

import pytest

from core.db.entities import Programme, Submission


@pytest.fixture()
def pathfinders_round_1_file_initial_validation_failures() -> BinaryIO:
    """An example spreadsheet for reporting round 1 of Pathfinders that should ingest with initial validation errors."""
    with open(Path(__file__).parent / "mock_pf_returns" / "PF_Round_1_Initial_Validation_Failures.xlsx", "rb") as file:
        yield file


@pytest.fixture()
def pathfinders_round_1_file_general_validation_failures() -> BinaryIO:
    """An example spreadsheet for reporting round 1 of Pathfinders that should ingest with validation errors."""
    with open(Path(__file__).parent / "mock_pf_returns" / "PF_Round_1_General_Validation_Failures.xlsx", "rb") as file:
        yield file


@pytest.fixture()
def pathfinders_round_1_file_cross_table_validation_failures() -> BinaryIO:
    """
    An example spreadsheet for reporting round 1 of Pathfinders that should ingest with cross table validation errors.
    """
    path = Path(__file__).parent / "mock_pf_returns" / "PF_Round_1_Cross_Table_Validation_Failures.xlsx"
    with open(path, "rb") as file:
        yield file


@pytest.fixture()
def pathfinders_round_1_file_general_and_cross_table_validation_failures() -> BinaryIO:
    """
    An example spreadsheet for reporting round 1 of Pathfinders that should ingest with general and cross table
    validation errors.
    """
    path = Path(__file__).parent / "mock_pf_returns" / "PF_Round_1_General_And_Cross_Table_Validation_Failures.xlsx"
    with open(path, "rb") as file:
        yield file


def test_ingest_pf_r1_file_success(test_client, pathfinders_round_1_file_success, test_buckets):
    """Tests that, given valid inputs, the endpoint responds successfully."""
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": pathfinders_round_1_file_success,
            "fund_name": "Pathfinders",
            "reporting_round": 1,
            "auth": json.dumps(
                {
                    "Programme": [
                        "Bolton Council",
                    ],
                    "Fund Types": [
                        "Pathfinders",
                    ],
                }
            ),
            "do_load": False,
        },
    )

    assert response.status_code == 200, f"{response.json}"
    assert response.json == {
        "detail": "Spreadsheet successfully validated but NOT ingested",
        "loaded": False,
        "metadata": {
            "FundType_ID": "PF",
            "Organisation": "Bolton Council",
            "Programme ID": "PF-BOL",
            "Programme Name": "Bolton Council",
        },
        "status": 200,
        "title": "success",
    }


def test_ingest_pf_r1_file_success_with_tf_data_already_in(
    test_client_reset,
    pathfinders_round_1_file_success,
    test_buckets,
    towns_fund_bolton_round_1_test_data,
):
    """Tests that Towns Fund data with a higher round does not take precedence over Pathfinders data."""

    endpoint = "/ingest"

    response = test_client_reset.post(
        endpoint,
        data={
            "excel_file": pathfinders_round_1_file_success,
            "fund_name": "Pathfinders",
            "reporting_round": 1,
            "auth": json.dumps(
                {
                    "Programme": [
                        "Bolton Council",
                    ],
                    "Fund Types": [
                        "Pathfinders",
                    ],
                }
            ),
            "do_load": True,
        },
    )

    assert response.status_code == 200, f"{response.json}"
    assert response.json == {
        "detail": "Spreadsheet successfully validated and ingested",
        "loaded": True,
        "metadata": {
            "FundType_ID": "PF",
            "Organisation": "Bolton Council",
            "Programme ID": "PF-BOL",
            "Programme Name": "Bolton Council",
        },
        "status": 200,
        "title": "success",
    }
    # ensure a new Programme and a new Submission are created for this Pathfinders submission
    assert len(Programme.query.all()) == 2
    assert len(Submission.query.all()) == 2

    # check submission id correctly generated
    assert len(Submission.query.filter(Submission.submission_id == "S-PF-R01-1").all()) == 1


def test_ingest_pf_r1_file_success_with_pf_submission_already_in(
    test_client_reset,
    pathfinders_round_1_file_success,
    test_buckets,
    pathfinders_round_1_submission_data,
):
    """Tests that the submission_id for Pathfinders increments by 1 when another programme for
    the same fund and round is already in the database."""

    endpoint = "/ingest"

    response = test_client_reset.post(
        endpoint,
        data={
            "excel_file": pathfinders_round_1_file_success,
            "fund_name": "Pathfinders",
            "reporting_round": 1,
            "auth": json.dumps(
                {
                    "Programme": [
                        "Bolton Council",
                    ],
                    "Fund Types": [
                        "Pathfinders",
                    ],
                }
            ),
            "do_load": True,
        },
    )

    assert response.status_code == 200, f"{response.json}"
    assert response.json == {
        "detail": "Spreadsheet successfully validated and ingested",
        "loaded": True,
        "metadata": {
            "FundType_ID": "PF",
            "Organisation": "Bolton Council",
            "Programme ID": "PF-BOL",
            "Programme Name": "Bolton Council",
        },
        "status": 200,
        "title": "success",
    }

    assert len(Submission.query.all()) == 2
    assert Submission.query.filter(Submission.submission_id == "S-PF-R01-2").first()


def test_ingest_pf_r1_auth_errors(test_client, pathfinders_round_1_file_success, test_buckets):
    """Tests that, with invalid auth params passed to ingest, the endpoint returns initial validation errors."""
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": pathfinders_round_1_file_success,
            "fund_name": "Pathfinders",
            "reporting_round": 1,
            "auth": json.dumps(
                {
                    "Programme": [
                        "Lewes District Council",
                    ],
                    "Fund Types": [
                        "Pathfinders",
                    ],
                }
            ),
            "do_load": False,
        },
    )

    assert response.status_code == 400, f"{response.json}"
    assert response.json["detail"] == "Workbook validation failed"
    assert len(response.json["pre_transformation_errors"]) == 1

    assert (
        "You’re not authorised to submit for Bolton Council. You can only submit for Lewes" " District Council."
    ) in response.json["pre_transformation_errors"]


def test_ingest_pf_r1_basic_initial_validation_errors(
    test_client, pathfinders_round_1_file_initial_validation_failures, test_buckets
):
    """Tests that, with incorrect values present in Excel file, the endpoint returns initial validation errors."""
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": pathfinders_round_1_file_initial_validation_failures,
            "fund_name": "Pathfinders",
            "reporting_round": 1,
            "auth": json.dumps(
                {
                    "Programme": [
                        "Rotherham Metropolitan Borough Council",
                    ],
                    "Fund Types": [
                        "Pathfinders",
                    ],
                }
            ),
            "do_load": False,
        },
    )

    assert response.status_code == 400, f"{response.json}"
    assert response.json["detail"] == "Workbook validation failed"
    assert len(response.json["pre_transformation_errors"]) == 2

    assert "The expected reporting round is 1" in response.json["pre_transformation_errors"]
    assert "You’re not authorised to submit for Pathfinders." in response.json["pre_transformation_errors"]


def test_ingest_pf_r1_general_validation_errors(
    test_client, pathfinders_round_1_file_general_validation_failures, test_buckets
):
    # TODO https://dluhcdigital.atlassian.net/browse/SMD-654: replace this test with a set of tests that check for
    #  specific errors once the template is stable
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": pathfinders_round_1_file_general_validation_failures,
            "fund_name": "Pathfinders",
            "reporting_round": 1,
            "auth": json.dumps(
                {
                    "Programme": [
                        "Bolton Council",
                    ],
                    "Fund Types": [
                        "Pathfinders",
                    ],
                }
            ),
            "do_load": False,
        },
    )

    assert response.status_code == 400, f"{response.json}"
    assert response.json["detail"] == "Workbook validation failed"
    validation_errors = response.json["validation_errors"]
    assert len(validation_errors) == 6
    expected_validation_errors = [
        {
            "cell_index": "B24",
            "description": "Enter a valid email address, for example, 'name.example@gmail.com'.",
            "error_type": None,
            "section": "Contact email",
            "sheet": "Admin",
        },
        {
            "cell_index": "B29",
            "description": (
                "Enter a valid UK telephone number starting with an apostrophe, for example, '01632 960 001, "
                "'07700 900 982 or '+44 808 157 0192"
            ),
            "error_type": None,
            "section": "Contact telephone",
            "sheet": "Admin",
        },
        {
            "cell_index": "B6",
            "description": "The cell is blank but is required.",
            "error_type": None,
            "section": "Portfolio progress",
            "sheet": "Progress",
        },
        {
            "cell_index": "G20",
            "description": "You entered text instead of a number. Remove any names of measurements and only use"
            " numbers, for example, '9'.",
            "error_type": None,
            "section": "Outputs",
            "sheet": "Outputs",
        },
        {
            "cell_index": "J47",
            "description": "Amount must be equal to or more than 0.",
            "error_type": None,
            "section": "Forecast and actual spend",
            "sheet": "Finances",
        },
        {
            "cell_index": "F9",
            "description": "You’ve entered your own content instead of selecting from the dropdown list provided. "
            "Select an option from the dropdown list.",
            "error_type": None,
            "section": "Risks",
            "sheet": "Risks",
        },
    ]
    assert validation_errors == expected_validation_errors


def test_ingest_pf_incorrect_round(test_client, pathfinders_round_1_file_success, test_buckets):
    """Tests that, with an incorrect reporting round, the endpoint throws an unhandled exception."""
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": pathfinders_round_1_file_success,
            "fund_name": "Pathfinders",
            "reporting_round": 2,
            "auth": json.dumps(
                {
                    "Programme": [
                        "Rotherham Metropolitan Borough Council",
                    ],
                    "Fund Types": [
                        "Pathfinders",
                    ],
                }
            ),
            "do_load": False,
        },
    )

    assert response.status_code == 400
    assert response.json["detail"] == "Ingest is not supported for Pathfinders round 2"


def test_ingest_pf_r1_cross_table_validation_errors(
    test_client, pathfinders_round_1_file_cross_table_validation_failures, test_buckets
):
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": pathfinders_round_1_file_cross_table_validation_failures,
            "fund_name": "Pathfinders",
            "reporting_round": 1,
            "auth": json.dumps(
                {
                    "Programme": [
                        "Bolton Council",
                    ],
                    "Fund Types": [
                        "Pathfinders",
                    ],
                }
            ),
            "do_load": False,
        },
    )

    assert response.status_code == 400, f"{response.json}"
    assert response.json["detail"] == "Workbook validation failed"
    validation_errors = response.json["validation_errors"]
    assert len(validation_errors) == 10
    expected_validation_errors = [
        {
            "cell_index": "B25",
            "description": "Project name 'Invalid project' is not allowed for this organisation.",
            "error_type": None,
            "section": "Project progress",
            "sheet": "Progress",
        },
        {
            "cell_index": "B15",
            "description": "Project name 'Invalid project' is not allowed for this organisation.",
            "error_type": None,
            "section": "Project location",
            "sheet": "Project location",
        },
        {
            "cell_index": "C21",
            "description": "Standard output value 'Invalid output' is not allowed for intervention theme"
            " 'Enhancing subregional and regional connectivity'.",
            "error_type": None,
            "section": "Outputs",
            "sheet": "Outputs",
        },
        {
            "cell_index": "D20",
            "description": "Unit of measurement 'Invalid standard output UoM'"
            " is not allowed for this output or outcome.",
            "error_type": None,
            "section": "Standard outputs",
            "sheet": "Outputs",
        },
        {
            "cell_index": "C20",
            "description": "Standard outcome value 'Invalid outcome' is not allowed for intervention theme"
            " 'Unlocking and enabling industrial commercial and residential development'.",
            "error_type": None,
            "section": "Outcomes",
            "sheet": "Outcomes",
        },
        {
            "cell_index": "C46",
            "description": "Bespoke output value 'Invalid bespoke output' is not allowed for this organisation.",
            "error_type": None,
            "section": "Bespoke outputs",
            "sheet": "Outputs",
        },
        {
            "cell_index": "C45",
            "description": "Bespoke outcome value 'Invalid bespoke outcome' is not allowed for this organisation.",
            "error_type": None,
            "section": "Bespoke outcomes",
            "sheet": "Outcomes",
        },
        {
            "cell_index": "B18",
            "description": "If you have selected 'Yes' for 'Credible Plan', you must answer Q2, Q3 and Q4.",
            "error_type": None,
            "section": "Total underspend",
            "sheet": "Finances",
        },
        {
            "cell_index": "E70",
            "description": "Intervention theme 'Not allowed' is not allowed.",
            "error_type": None,
            "section": "Project finance changes",
            "sheet": "Finances",
        },
        {
            "cell_index": "P70",
            "description": "Reporting period must be in the future if 'Actual, forecast or cancelled' is 'Forecast'.",
            "error_type": None,
            "section": "Project finance changes",
            "sheet": "Finances",
        },
    ]
    assert validation_errors == expected_validation_errors


def test_ingest_pf_r1_general_and_cross_table_validation_errors(
    test_client, pathfinders_round_1_file_general_and_cross_table_validation_failures, test_buckets
):
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": pathfinders_round_1_file_general_and_cross_table_validation_failures,
            "fund_name": "Pathfinders",
            "reporting_round": 1,
            "auth": json.dumps(
                {
                    "Programme": [
                        "Bolton Council",
                    ],
                    "Fund Types": [
                        "Pathfinders",
                    ],
                }
            ),
            "do_load": False,
        },
    )

    assert response.status_code == 400, f"{response.json}"
    assert response.json["detail"] == "Workbook validation failed"
    validation_errors = response.json["validation_errors"]
    assert len(validation_errors) == 2
    expected_validation_errors = [
        {
            "cell_index": "B24",
            "description": "Enter a valid email address, for example, 'name.example@gmail.com'.",
            "error_type": None,
            "section": "Contact email",
            "sheet": "Admin",
        },
        {
            "cell_index": "B18",
            "description": "If you have selected 'Yes' for 'Credible Plan', you must answer Q2, Q3 and Q4.",
            "error_type": None,
            "section": "Total underspend",
            "sheet": "Finances",
        },
    ]
    assert validation_errors == expected_validation_errors
