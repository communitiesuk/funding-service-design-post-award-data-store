import json
from pathlib import Path
from typing import BinaryIO

import pandas as pd
import pytest
from flask.testing import FlaskClient
from werkzeug.datastructures import FileStorage

from core.const import EXCEL_MIMETYPE
from core.controllers.ingest import extract_data
from core.validation.failures import ExtraSheetFailure

resources = Path(__file__).parent / "resources"


@pytest.fixture(scope="function")
def wrong_format_test_file() -> BinaryIO:
    """An invalid text test file."""
    with open(resources / "wrong_format_test_file.txt", "rb") as file:
        yield file


"""
/ingest endpoint validation_tests
"""


def test_ingest_endpoint(app: FlaskClient, example_data_model_file):
    """Tests that, given valid inputs, the endpoint responds successfully."""
    endpoint = "/ingest"
    response = app.post(
        endpoint,
        data={
            "excel_file": example_data_model_file,
        },
    )

    assert response.status_code == 200, f"{response.json}"


def test_ingest_endpoint_missing_file(app: FlaskClient):
    """Tests that, given a sheet name but no file, the endpoint returns a 400 error."""
    endpoint = "/ingest"
    response = app.post(
        endpoint,
        data={},  # empty body
    )

    decoded_response = json.loads(response.data.decode())
    assert response.status_code == 400
    assert decoded_response == {
        "detail": "'excel_file' is a required property",
        "status": 400,
        "title": "Bad Request",
        "type": "about:blank",
    }


def test_ingest_endpoint_returns_validation_errors(app: FlaskClient, example_data_model_file, mocker):
    """
    Tests that, given valid request params but an invalid workbook,
    the endpoint returns a 400 validation error with the validation error message.
    """

    # mock validate response to return an error
    mocker.patch("core.controllers.ingest.validate", return_value=[ExtraSheetFailure(extra_sheet="MockedExtraSheet")])

    endpoint = "/ingest"
    response = app.post(
        endpoint,
        data={
            "excel_file": example_data_model_file,  # only passed to get passed the missing file check
        },
    )

    assert response.status_code == 400
    assert response.json["detail"] == "Workbook validation failed"
    assert isinstance(response.json["validation_errors"], list)
    assert len(response.json["validation_errors"]) == 1


def test_ingest_endpoint_invalid_file_type(app: FlaskClient, wrong_format_test_file):
    """
    Tests that, given a file of the wrong format, the endpoint returns a 400 error.
    """
    endpoint = "/ingest"
    response = app.post(
        endpoint,
        data={
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


def test_multiple_ingests(app: FlaskClient, example_data_model_file):
    endpoint = "/ingest"

    # Ingest once
    first_response = app.post(
        endpoint,
        data={
            "schema": "towns_fund",
            "excel_file": example_data_model_file,
        },
    )
    # check endpoint gave a success response to ingest
    assert first_response.status_code == 200

    # Ingest twice
    with open(resources / "Data_Model_v3.7_EXAMPLE.xlsx", "rb") as another_example_file:
        # ingest example data spreadsheet
        second_response = app.post(
            endpoint,
            data={
                "schema": "towns_fund",
                "excel_file": another_example_file,
            },
        )

    # check endpoint gave a success response to ingest
    assert second_response.status_code == 200


def test_extract_data_extracts_from_multiple_sheets(example_data_model_file):
    file = FileStorage(example_data_model_file, content_type=EXCEL_MIMETYPE)
    workbook = extract_data(file)

    assert len(workbook) > 1
    assert isinstance(workbook, dict)
    assert isinstance(list(workbook.values())[0], pd.DataFrame)
