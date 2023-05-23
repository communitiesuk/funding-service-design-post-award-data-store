from typing import BinaryIO

import pandas as pd
import pytest
from flask.testing import FlaskClient

from core.extraction.round_two import ingest_round_two_data
from core.extraction.towns_fund import ingest_towns_fund_data

# isort: off
from tests.controller_tests.resources.response_assertion_data import (
    MOCK_PACKAGE_RESPONSE,
    MOCK_PROJECT_RESPONSE,
)


@pytest.fixture()
def ingested_test_client(flask_test_client: FlaskClient, example_file: BinaryIO):
    """Setup test client by running ingest on example data."""
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


def test_get_packages(ingested_test_client: FlaskClient):
    """Test package API endpoint responses on data ingested via ingest API."""

    unmatched_package_response = ingested_test_client.get("/package/LUF01")
    assert unmatched_package_response.status_code == 404

    valid_package_id = "FHSF001"

    package_response = ingested_test_client.get("/package/" + valid_package_id)
    assert package_response.status_code == 200
    assert package_response.json == MOCK_PACKAGE_RESPONSE


# TODO: Remove / update this test once ingest connected into main work-flow
@pytest.mark.skip(reason="currently this is just a pytest/pycharm debug entrypoint for ingest work")
def test_ingest_towns_fund_template():
    towns_fund_data = pd.read_excel(
        "EXAMPLE_TF_Reporting_Template_-_TD_-_Newhaven_-_DDMMYY.xlsx",
        sheet_name=None,  # extract from all sheets
    )
    ingest_towns_fund_data(towns_fund_data)


def test_ingest_round_two_historical():
    # TODO: currently testing with small subset of data (to allow reasonable debugging speed)
    round_two_data = pd.read_excel(
        "Round 2 Reporting - Consolidation - subset.xlsx",
        sheet_name=None,  # extract from all sheets
    )
    ingest_round_two_data(round_two_data)
