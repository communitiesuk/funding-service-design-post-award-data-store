import json
from pathlib import Path
from typing import BinaryIO

import pytest
from flask.testing import FlaskClient

resources = Path(__file__).parent / "resources"


@pytest.fixture()
def ingest_test_client(flask_test_client: FlaskClient):
    flask_test_client.application.config["SCHEMAS"] = {
        "towns_fund": {
            "TestSheet": {
                "columns": {
                    "Field 1": "string",
                    "Field 2": "int64",
                    "Field 3": "datetime64[ns]",
                },
                "uniques": ["Field 1", "Field 2"],
            },
        }
    }
    yield flask_test_client


@pytest.fixture(scope="function")
def test_file() -> BinaryIO:
    """A valid Excel test file."""
    return (resources / "test_file.xlsx").open("rb")


@pytest.fixture(scope="function")
def empty_test_file() -> BinaryIO:
    """A valid Excel test file."""
    return (resources / "empty_test_file.xlsx").open("rb")


@pytest.fixture(scope="function")
def invalid_test_file() -> BinaryIO:
    """An invalid Excel test file."""
    return (resources / "invalid_test_file.xlsx").open("rb")


@pytest.fixture(scope="function")
def wrong_format_test_file() -> BinaryIO:
    """An invalid text test file."""
    return (resources / "wrong_format_test_file.txt").open("rb")


"""
/ingest endpoint validation_tests
"""


def test_ingest_endpoint(ingest_test_client: FlaskClient, test_file):
    """Tests that, given valid inputs, the endpoint responds successfully."""
    endpoint = "/ingest"
    response = ingest_test_client.post(
        endpoint,
        data={
            "schema": "towns_fund",
            "sheet_names": ["TestSheet"],
            "excel_file": test_file,
        },
    )

    assert response.status_code == 200
    assert set(json.loads(response.data.decode().strip()).keys()) == {"TestSheet"}


def test_ingest_endpoint_empty_sheet(
    ingest_test_client: FlaskClient, empty_test_file: BinaryIO
):
    """
    Tests that, given valid inputs and an empty Excel sheet,
    the endpoint returns a validation error.
    """
    ingest_test_client.application.config["SCHEMAS"] = {
        "towns_fund": {
            "EmptySheet": {
                "columns": {},
            },
        }
    }
    endpoint = "/ingest"
    response = ingest_test_client.post(
        endpoint,
        data={
            "schema": "towns_fund",
            "sheet_names": ["EmptySheet"],
            "excel_file": empty_test_file,
        },
    )

    decoded_response = json.loads(response.data.decode().strip())
    assert response.status_code == 400
    assert decoded_response["detail"] == "Workbook validation failed"
    assert isinstance(decoded_response["validation_errors"], list)
    assert len(decoded_response["validation_errors"]) == 1


def test_ingest_endpoint_invalid_workbook(
    ingest_test_client: FlaskClient, invalid_test_file: BinaryIO
):
    """
    Tests that, given a valid request but an invalid workbook,
    the endpoint returns validation errors.
    """
    endpoint = "/ingest"
    response = ingest_test_client.post(
        endpoint,
        data={
            "schema": "towns_fund",
            "sheet_names": ["TestSheet"],
            "excel_file": invalid_test_file,
        },
    )

    decoded_response = json.loads(response.data.decode().strip())
    assert response.status_code == 400
    assert decoded_response["detail"] == "Workbook validation failed"
    assert isinstance(decoded_response["validation_errors"], list)
    assert len(decoded_response["validation_errors"]) == 3


def test_ingest_endpoint_missing_sheet_names(
    ingest_test_client: FlaskClient, test_file
):
    """Tests that given a file but no sheet name, the endpoint response successfully."""
    endpoint = "/ingest"
    response = ingest_test_client.post(
        endpoint,
        data={
            "schema": "towns_fund",
            "excel_file": test_file,
        },
    )

    assert response.status_code == 200
    assert set(json.loads(response.data.decode().strip()).keys()) == {"TestSheet"}


def test_ingest_endpoint_missing_file(ingest_test_client: FlaskClient):
    """Tests that, given a sheet name but no file, the endpoint returns a 400 error."""
    endpoint = "/ingest"
    response = ingest_test_client.post(
        endpoint,
        data={
            "schema": "towns_fund",
            "sheet_names": ["TestSheet"],
        },
    )

    decoded_response = json.loads(response.data.decode())
    assert response.status_code == 400
    assert decoded_response == {
        "detail": "'excel_file' is a required property",
        "status": 400,
        "title": "Bad Request",
        "type": "about:blank",
    }


def test_ingest_endpoint_invalid_file_type(
    ingest_test_client: FlaskClient, wrong_format_test_file
):
    """
    Tests that, given a file of the wrong format, the endpoint returns a 400 error.
    """
    endpoint = "/ingest"
    response = ingest_test_client.post(
        endpoint,
        data={
            "schema": "towns_fund",
            "sheet_names": ["TestSheet"],
            "excel_file": wrong_format_test_file,
        },
    )

    decoded_response = json.loads(response.data.decode())
    assert response.status_code == 400
    assert decoded_response == {
        "detail": "Invalid file type",
        "status": 400,
        "title": "Bad Request",
        "type": "about:blank",
    }


def test_ingest_endpoint_does_not_contain_sheet(
    ingest_test_client: FlaskClient, test_file
):
    """
    Tests that, given a file that does not contain the specified sheet name,
    the endpoint returns a 400 error.
    """
    endpoint = "/ingest"
    response = ingest_test_client.post(
        endpoint,
        data={
            "schema": "towns_fund",
            "sheet_names": ["NonExistentTestSheet"],
            "excel_file": test_file,
        },
    )

    decoded_response = json.loads(response.data.decode())
    assert response.status_code == 400
    assert decoded_response == {
        "detail": "Invalid array of sheet names",
        "status": 400,
        "title": "Bad Request",
        "type": "about:blank",
    }
