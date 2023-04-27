from pathlib import Path
from typing import BinaryIO

import pytest
from flask.testing import FlaskClient

# isort: off
from tests.controller_tests.resources.response_assertion_data import (
    MOCK_PACKAGE_RESPONSE,
    MOCK_PROJECT_RESPONSE,
)

resources = Path(__file__).parent / "resources"


@pytest.fixture(scope="function")
def example_file() -> BinaryIO:
    """An example spreadsheet in towns-fund schema format."""
    return (resources / "DLUCH_Data_Model_V3.4_EXAMPLE.xlsx").open("rb")


@pytest.fixture()
def ingested_test_client(flask_test_client: FlaskClient, example_file):
    """Setup test client by running ingest on example data."""

    # ingest example data spreadsheet
    endpoint = "/ingest"
    response = flask_test_client.post(
        endpoint,
        data={
            "schema": "towns_fund",
            "excel_file": example_file,
        },
    )
    # check endpoint gave a success response to ingest
    assert response.status_code == 200
    yield flask_test_client


def test_get_projects(ingested_test_client: FlaskClient):
    """Test project API endpoint responses on data ingested via ingest API."""

    unmatched_project_response = ingested_test_client.get("/project/LUF01")
    assert unmatched_project_response.status_code == 404

    valid_project_id = "FHSFDCC001"

    project_response = ingested_test_client.get("/project/" + valid_project_id)

    # check response contains expected data structure
    assert project_response.status_code == 200
    assert project_response.json == MOCK_PROJECT_RESPONSE
    assert project_response.json["project_id"] == valid_project_id

    # sanity check - only data with requested project id references are returned
    for sheet in project_response.json:
        if isinstance(sheet, list):
            for row in sheet:
                assert row["project_id"] == valid_project_id


def test_get_packages(ingested_test_client: FlaskClient):
    """Test package API endpoint responses on data ingested via ingest API."""

    unmatched_package_response = ingested_test_client.get("/package/LUF01")
    assert unmatched_package_response.status_code == 404

    valid_package_id = "FHSF001"

    package_response = ingested_test_client.get("/package/" + valid_package_id)
    assert package_response.status_code == 200
    assert package_response.json == MOCK_PACKAGE_RESPONSE
    assert package_response.json["package_id"] == valid_package_id
