"""
Contains fixtures shared across Round 3 and Round 4 extraction pipelines.
"""

from pathlib import Path

import pandas as pd
import pytest

from data_store.transformation.towns_fund import tf_transform_r3 as tf

round_3_resources_mocks = Path(__file__).parent / "resources" / "mock_sheet_data" / "round_three"


@pytest.fixture(scope="module")
def fund_code():
    """Return fund code."""
    return "TD"


@pytest.fixture(scope="module")
def mock_start_here_sheet():
    """Setup mock start here sheet."""
    test_start_sheet = pd.read_csv(round_3_resources_mocks / "start_page_mock.csv", header=None, index_col=None)

    return test_start_sheet


@pytest.fixture(scope="module")
def mock_project_admin_sheet():
    """Setup mock project_admin sheet."""
    test_project_sheet = pd.read_csv(
        round_3_resources_mocks / "project_admin_sheet_mock.csv", header=None, index_col=None
    )

    return test_project_sheet


@pytest.fixture(scope="module")
def mock_project_identifiers_sheet():
    """Setup mock project identifiers sheet."""
    test_project_identifiers_sheet = pd.read_csv(
        round_3_resources_mocks / "project_identifiers_mock.csv", header=None, index_col=None
    )

    return test_project_identifiers_sheet


@pytest.fixture(scope="module")
def mock_hs_project_identifiers_sheet():
    """Setup mock project identifiers sheet."""
    test_hs_project_identifiers_sheet = pd.read_csv(
        round_3_resources_mocks / "project_identifiers_HS_mock.csv", header=None, index_col=None
    )

    return test_hs_project_identifiers_sheet


@pytest.fixture
def mock_place_identifiers_sheet():
    """Setup mock project identifiers sheet."""
    test_place_identifiers_sheet = pd.read_csv(
        round_3_resources_mocks / "place_identifiers_mock.csv", header=None, index_col=None
    )

    return test_place_identifiers_sheet


@pytest.fixture(scope="module")
def mock_funding_sheet():
    """Load mock funding sheet into dataframe from csv."""
    test_funding_df = pd.read_csv(round_3_resources_mocks / "funding_profiles_mock.csv", header=None, index_col=None)

    return test_funding_df


@pytest.fixture(scope="module")
def mock_hs_funding_sheet():
    """Load mock funding sheet into dataframe from csv."""
    test_funding_df = pd.read_csv(round_3_resources_mocks / "funding_profiles_HS_mock.csv", header=None, index_col=None)

    return test_funding_df


@pytest.fixture(scope="module")
def mock_psi_sheet():
    """Load mock private investments sheet into dataframe from csv."""
    test_psi_df = pd.read_csv(round_3_resources_mocks / "psi_mock.csv", header=None, index_col=None)

    return test_psi_df


@pytest.fixture(scope="module")
def mock_outputs_sheet():
    """Load fake project outputs sheet into dataframe from csv."""
    test_outputs_df = pd.read_csv(round_3_resources_mocks / "outputs_mock.csv", header=None, index_col=None)

    return test_outputs_df


@pytest.fixture(scope="module")
def mock_outcomes_sheet():
    """Load fake project outcomes sheet into dataframe from csv."""
    test_outcomes_df = pd.read_csv(round_3_resources_mocks / "outcomes_mock.csv", header=None, index_col=None)

    return test_outcomes_df


@pytest.fixture(scope="module")
def mock_risk_sheet():
    """Load fake risk sheet into dataframe, from csv."""
    test_risk_df = pd.read_csv(round_3_resources_mocks / "risk_mock.csv", header=None, index_col=None)

    return test_risk_df


@pytest.fixture
def mock_place_extract(mock_project_admin_sheet):
    """Setup test place sheet extract."""
    test_place = mock_project_admin_sheet
    return tf.extract_place_details(test_place)


@pytest.fixture
def mock_project_lookup(mock_project_identifiers_sheet, mock_place_extract, fund_code):
    """Setup mock project lookup table"""
    return tf.extract_project_lookup(mock_project_identifiers_sheet, mock_place_extract, fund_code)


@pytest.fixture
def mock_hs_project_lookup(mock_hs_project_identifiers_sheet, mock_place_extract, fund_code):
    """Setup mock project lookup table"""
    return tf.extract_project_lookup(mock_hs_project_identifiers_sheet, mock_place_extract, fund_code)


@pytest.fixture
def mock_programme_lookup(mock_place_identifiers_sheet, mock_place_extract, fund_code):
    """Setup mock programme lookup value."""
    test_programme = tf.get_programme_id(mock_place_identifiers_sheet, mock_place_extract, fund_code)
    assert test_programme == "TD-FAK"
    return test_programme
