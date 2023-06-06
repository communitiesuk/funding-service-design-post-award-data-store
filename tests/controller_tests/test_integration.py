import pandas as pd
import pytest
from flask.testing import FlaskClient

from core.extraction.round_one import ingest_round_1_data
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


# TODO: Remove / update this test once ingest connected into main work-flow
@pytest.mark.skip(reason="currently this is just a pytest/pycharm debug entrypoint for ingest work")
def test_ingest_round_one_historical():
    # assumes that Round 1 Reporting data has had the tab 'Place Identifiers' added from EXAMPLE_TF_REPORTING_TEMPLATE
    towns_fund_data = pd.read_excel("Round 1 Reporting - TF_aggregated_data_23.09.2022.xlsx", sheet_name=None)
    data_model = pd.read_excel("Data Model v3.7.xlsx", sheet_name=None)

    ingest_round_1_data(towns_fund_data, data_model)
