import json
from pathlib import Path
from typing import BinaryIO

import pandas as pd
import pytest
from flask.testing import FlaskClient
from werkzeug.datastructures import FileStorage

from core.controllers.ingest import EXCEL_MIMETYPE, extract_data

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
            "Another Sheet": {
                "columns": {
                    "Field 1": "string",
                    "Field 2": "string",
                }
            },
        }
    }
    yield flask_test_client


@pytest.fixture(scope="function")
def test_file() -> BinaryIO:
    """A valid Excel test file."""
    with open(resources / "test_file.xlsx", "rb") as file:
        yield file


@pytest.fixture(scope="function")
def empty_test_file() -> BinaryIO:
    """A valid Excel test file."""
    with open(resources / "empty_test_file.xlsx", "rb") as file:
        yield file


@pytest.fixture(scope="function")
def invalid_test_file() -> BinaryIO:
    """An invalid Excel test file."""
    with open(resources / "invalid_test_file.xlsx", "rb") as file:
        yield file


@pytest.fixture(scope="function")
def wrong_format_test_file() -> BinaryIO:
    """An invalid text test file."""
    with open(resources / "wrong_format_test_file.txt", "rb") as file:
        yield file


"""
/ingest endpoint validation_tests
"""


def test_ingest_endpoint(flask_test_client: FlaskClient, example_file):
    """Tests that, given valid inputs, the endpoint responds successfully."""
    endpoint = "/ingest"
    response = flask_test_client.post(
        endpoint,
        data={
            "schema": "towns_fund",
            "excel_file": example_file,
        },
    )

    assert response.status_code == 200


def test_ingest_endpoint_empty_sheet(ingest_test_client: FlaskClient, empty_test_file: BinaryIO):
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
            "excel_file": empty_test_file,
        },
    )

    decoded_response = json.loads(response.data.decode().strip())
    assert response.status_code == 400
    assert decoded_response["detail"] == "Workbook validation failed"
    assert decoded_response["validation_errors"]
    assert isinstance(decoded_response["validation_errors"], list)


def test_ingest_endpoint_invalid_workbook(ingest_test_client: FlaskClient, invalid_test_file: BinaryIO):
    """
    Tests that, given a valid request but an invalid workbook,
    the endpoint returns validation errors.
    """
    endpoint = "/ingest"
    response = ingest_test_client.post(
        endpoint,
        data={
            "schema": "towns_fund",
            "excel_file": invalid_test_file,
        },
    )

    decoded_response = json.loads(response.data.decode().strip())
    assert response.status_code == 400
    assert decoded_response["detail"] == "Workbook validation failed"
    assert decoded_response["validation_errors"]
    assert isinstance(decoded_response["validation_errors"], list)


def test_ingest_endpoint_missing_file(ingest_test_client: FlaskClient):
    """Tests that, given a sheet name but no file, the endpoint returns a 400 error."""
    endpoint = "/ingest"
    response = ingest_test_client.post(
        endpoint,
        data={
            "schema": "towns_fund",
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


def test_ingest_endpoint_invalid_file_type(ingest_test_client: FlaskClient, wrong_format_test_file):
    """
    Tests that, given a file of the wrong format, the endpoint returns a 400 error.
    """
    endpoint = "/ingest"
    response = ingest_test_client.post(
        endpoint,
        data={
            "schema": "towns_fund",
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


def test_multiple_ingests(flask_test_client: FlaskClient, example_file: BinaryIO):
    endpoint = "/ingest"

    # Ingest once
    first_response = flask_test_client.post(
        endpoint,
        data={
            "schema": "towns_fund",
            "excel_file": example_file,
        },
    )
    # check endpoint gave a success response to ingest
    assert first_response.status_code == 200

    # Ingest twice
    with open(resources / "DLUCH_Data_Model_V3.4_EXAMPLE.xlsx", "rb") as another_example_file:
        # ingest example data spreadsheet
        second_response = flask_test_client.post(
            endpoint,
            data={
                "schema": "towns_fund",
                "excel_file": another_example_file,
            },
        )

    # check endpoint gave a success response to ingest
    assert second_response.status_code == 200


def test_extract_data_extracts_from_multiple_sheets(test_file):
    file = FileStorage(test_file, content_type=EXCEL_MIMETYPE)
    workbook = extract_data(file)

    assert len(workbook) > 1
    assert isinstance(workbook, dict)
    assert isinstance(list(workbook.values())[0], pd.DataFrame)
