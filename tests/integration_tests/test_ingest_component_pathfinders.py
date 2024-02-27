import json
from pathlib import Path
from typing import BinaryIO

import pytest


@pytest.fixture()
def pathfinders_round_1_file_success() -> BinaryIO:
    """An example spreadsheet for reporting round 4 of Towns Fund that should ingest without validation errors."""
    with open(Path(__file__).parent / "mock_pf_returns" / "PF_Round_1_Success.xlsx", "rb") as file:
        yield file


@pytest.fixture()
def pathfinders_round_1_file_failure() -> BinaryIO:
    """An example spreadsheet for reporting round 4 of Towns Fund that should ingest without validation errors."""
    with open(Path(__file__).parent / "mock_pf_returns" / "PF_Round_1_Failure.xlsx", "rb") as file:
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

    assert response.status_code == 200, f"{response.json}"
    assert response.json == {
        "detail": "PF initial validation success",
        "loaded": False,
    }


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
        "You’re not authorised to submit for Rotherham Metropolitan Borough Council. You can only submit for Lewes"
        " District Council."
    ) in response.json["pre_transformation_errors"]


def test_ingest_pf_r1_basic_errors(test_client, pathfinders_round_1_file_failure, test_buckets):
    """Tests that, with incorrect values present in Excel file, the endpoint returns initial validation errors."""
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": pathfinders_round_1_file_failure,
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


def test_ingest_pf_incorrect_round(test_client, pathfinders_round_1_file_success, test_buckets):
    """Tests that, with an incorrect reporting round, the endpoint throws an unhandled exception."""
    # TODO is this the desired behaviour?
    with pytest.raises(ValueError) as e:
        endpoint = "/ingest"
        test_client.post(
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

    assert e.value.args == ("There are no IngestDependencies for Pathfinders round 2",)
