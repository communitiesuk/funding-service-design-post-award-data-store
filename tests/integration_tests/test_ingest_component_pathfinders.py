import json
from pathlib import Path
from typing import BinaryIO

import pytest

from core.db.entities import Programme, Submission


@pytest.fixture()
def pathfinders_round_1_file_success() -> BinaryIO:
    """An example spreadsheet for reporting round 4 of Towns Fund that should ingest without validation errors."""
    with open(Path(__file__).parent / "mock_pf_returns" / "PF_Round_1_Success.xlsx", "rb") as file:
        yield file


@pytest.fixture()
def pathfinders_round_1_file_initial_validation_failure() -> BinaryIO:
    """An example spreadsheet for reporting round 1 of Pathfinders that should ingest without validation errors."""
    with open(Path(__file__).parent / "mock_pf_returns" / "PF_Round_1_Initial_Validation_Failure.xlsx", "rb") as file:
        yield file


@pytest.fixture()
def pathfinders_round_1_file_success_same_programme_as_towns_fund() -> BinaryIO:
    """An example spreadsheet for reporting round 1 of Pathfinders sharing a programme with towns fund round 3."""
    with open(Path(__file__).parent / "mock_pf_returns" / "PF_Round_1_Same_Programme_As_TF_Round_3.xlsx", "rb") as file:
        yield file


@pytest.fixture()
def towns_fund_round_3_file_success_same_programme_as_pathfinders() -> BinaryIO:
    """An example spreadsheet for reporting round 3 of towns fund sharing a programme with pathfinders round 1."""
    with open(
        Path(__file__).parent / "mock_tf_returns" / "TF_Round_3_Success_Same_Prog_As_PF_Round_1.xlsx", "rb"
    ) as file:
        yield file


@pytest.fixture()
def pathfinders_round_1_file_validation_failure() -> BinaryIO:
    """An example spreadsheet for reporting round 1 of Pathfinders that should ingest with validation errors."""
    with open(Path(__file__).parent / "mock_pf_returns" / "PF_Round_1_Validation_Failures.xlsx", "rb") as file:
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
                        "Bolton Metropolitan Borough Council",
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
            "Organisation": "Bolton Metropolitan Borough Council",
            "Programme ID": "PF-BOL",
            "Programme Name": "Bolton Metropolitan Borough Council",
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
                        "Bolton Metropolitan Borough Council",
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
            "Organisation": "Bolton Metropolitan Borough Council",
            "Programme ID": "PF-BOL",
            "Programme Name": "Bolton Metropolitan Borough Council",
        },
        "status": 200,
        "title": "success",
    }
    # ensure a new Programme and a new Submission are created for this Pathfinders submission
    assert len(Programme.query.all()) == 2
    assert len(Submission.query.all()) == 2


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
        "You’re not authorised to submit for Bolton Metropolitan Borough Council. You can only submit for Lewes"
        " District Council."
    ) in response.json["pre_transformation_errors"]


def test_ingest_pf_r1_basic_initial_validation_errors(
    test_client, pathfinders_round_1_file_initial_validation_failure, test_buckets
):
    """Tests that, with incorrect values present in Excel file, the endpoint returns initial validation errors."""
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": pathfinders_round_1_file_initial_validation_failure,
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

    assert "The expected reporting period is Q3 Oct - Dec 23/24" in response.json["pre_transformation_errors"]
    assert "The expected value is V 1.0" in response.json["pre_transformation_errors"]


def test_ingest_pf_r1_general_validation_errors(test_client, pathfinders_round_1_file_validation_failure, test_buckets):
    # TODO https://dluhcdigital.atlassian.net/browse/SMD-654: replace this test with a set of tests that check for
    #  specific errors once the template is stable
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": pathfinders_round_1_file_validation_failure,
            "fund_name": "Pathfinders",
            "reporting_round": 1,
            "auth": json.dumps(
                {
                    "Programme": [
                        "Bolton Metropolitan Borough Council",
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
    assert len(validation_errors) == 4
    expected_validation_errors = [
        {
            "cell_index": "B24",
            "description": "Please enter a valid email address.",
            "error_type": None,
            "section": None,
            "sheet": "Admin",
        },
        {
            "cell_index": "F20",
            "description": "You entered text instead of a number. Remove any units of measurement and only use numbers,"
            " for example, 9.",
            "error_type": None,
            "section": None,
            "sheet": "Outputs",
        },
        {
            "cell_index": "J42",
            "description": "Amount must be positive.",
            "error_type": None,
            "section": None,
            "sheet": "Finances",
        },
        {
            "cell_index": "F9",
            "description": "You’ve entered your own content, instead of selecting from the dropdown list provided. "
            "Select an option from the dropdown list.",
            "error_type": None,
            "section": None,
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
