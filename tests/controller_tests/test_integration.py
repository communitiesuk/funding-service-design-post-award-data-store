import pandas as pd
import pytest
from flask.testing import FlaskClient

from core.extraction.round_two import ingest_round_two_data
from core.extraction.towns_fund import ingest_towns_fund_data


@pytest.fixture()
def ingested_test_client(app: FlaskClient, example_data_model_file):
    """Setup test client by running ingest on example data."""
    endpoint = "/ingest"
    response = app.post(
        endpoint,
        data={
            "excel_file": example_data_model_file,
        },
    )
    # check endpoint gave a success response to ingest
    assert response.status_code == 200
    yield app


def test_get_projects(ingested_test_client: FlaskClient):
    """Test project API endpoint responses on data ingested via ingest API."""

    unmatched_project_response = ingested_test_client.get("/project/LUF01")
    assert unmatched_project_response.status_code == 404

    valid_project_id = "FHSFDCC001"

    project_response = ingested_test_client.get("/project/" + valid_project_id)

    assert project_response.status_code == 200
    assert project_response.json  # check it returns something but don't assert on the contents


def test_get_programmes(ingested_test_client: FlaskClient):
    """Test programme API endpoint responses on data ingested via ingest API."""

    unmatched_programme_response = ingested_test_client.get("/programme/LUF01")
    assert unmatched_programme_response.status_code == 404

    valid_programme_id = "FHSF001"

    programme_response = ingested_test_client.get("/programme/" + valid_programme_id)

    assert programme_response.status_code == 200
    assert programme_response.json  # check it returns something but don't assert on the contents


# TODO: Remove / update this test once ingest connected into main work-flow
@pytest.mark.skip(reason="currently this is just a pytest/pycharm debug entrypoint for ingest work")
def test_ingest_towns_fund_template():
    towns_fund_data = pd.read_excel(
        "EXAMPLE_TF_Reporting_Template_-_TD_-_Newhaven_-_DDMMYY.xlsx",
        sheet_name=None,  # extract from all sheets
    )
    ingest_towns_fund_data(towns_fund_data)


@pytest.mark.skip(reason="currently this is just a pytest/pycharm debug entrypoint for ingest work")
def test_ingest_round_two_historical():
    # TODO: currently testing with small subset of data (to allow reasonable debugging speed)
    round_two_data = pd.read_excel(
        "Round 2 Reporting - Consolidation - subset.xlsx",
        # "Round 2 Reporting - Consolidation.xlsx",
        sheet_name=None,  # extract from all sheets
    )
    ingest_round_two_data(round_two_data["December 2022"])
