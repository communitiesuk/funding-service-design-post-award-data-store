"""
Round 4 extraction is almost identical to Round 3 and so re-uses many components.

The tests in this module cover new functionality unique to Round 4.
"""
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
from pandas._testing import assert_frame_equal

import core.extraction.towns_fund_round_three as tf
from core.controllers.mappings import INGEST_MAPPINGS
from core.extraction.towns_fund_round_four import (
    extract_programme_progress,
    ingest_round_four_data_towns_fund,
)

resources = Path(__file__).parent / "resources"
resources_mocks = resources / "mock_sheet_data" / "round_four"
resources_assertions = resources / "assertion_data" / "round_four"


@pytest.fixture
def mock_progress_sheet():
    """Setup mock programme/project progress sheet.

    Ignores time conversions from Excel to Python (lost in process of saving mock data as csv)."""
    test_progress_df = pd.read_csv(resources_mocks / "programme_progress_mock.csv")

    return test_progress_df


@pytest.fixture
def mock_ingest_full_sheet(
    mock_start_here_sheet,
    mock_project_admin_sheet,
    mock_progress_sheet,
    mock_project_identifiers_sheet,
    mock_place_identifiers_sheet,
    mock_funding_sheet,
    mock_psi_sheet,
    mock_outputs_sheet,
    mock_outcomes_sheet,
    mock_risk_sheet,
):
    """
    Load all fake fixture data into dict via ingest_towns_fund_data.

    Set up a fake dict of dataframes that mimics the Towns Fund V4.0 Excel sheet ingested directly into Pandas.
    """
    mock_df_ingest = {
        "1 - Start Here": mock_start_here_sheet,
        "2 - Project Admin": mock_project_admin_sheet,
        "3 - Programme Progress": mock_progress_sheet,
        "4a - Funding Profiles": mock_funding_sheet,
        "4b - PSI": mock_psi_sheet,
        "5 - Project Outputs": mock_outputs_sheet,
        "6 - Outcomes": mock_outcomes_sheet,
        "7 - Risk Register": mock_risk_sheet,
        "Project Identifiers": mock_project_identifiers_sheet,
        "Place Identifiers": mock_place_identifiers_sheet,
    }

    return mock_df_ingest


@pytest.fixture
@patch("core.extraction.towns_fund_round_three.TF_PLACE_NAMES_TO_ORGANISATIONS", {"Fake Town": "Fake Canonical Org"})
def mock_ingest_full_extract(mock_ingest_full_sheet):
    """Setup mock of full spreadsheet extract."""

    return ingest_round_four_data_towns_fund(mock_ingest_full_sheet)


def test_extract_programme_progress(mock_progress_sheet, mock_programme_lookup):
    """Test programme progress rows extracted as expected."""
    extracted_programme_progress = extract_programme_progress(mock_progress_sheet, mock_programme_lookup)
    expected_programme_progress = pd.read_csv(resources_assertions / "programme_progress_expected.csv")
    assert_frame_equal(extracted_programme_progress, expected_programme_progress)


def test_extract_project_progress(mock_progress_sheet, mock_project_lookup):
    """Test project progress rows extracted as expected."""
    # round four parameter set to true
    extracted_project_progress = tf.extract_project_progress(mock_progress_sheet, mock_project_lookup, round_four=True)
    expected_project_progress = pd.read_csv(resources_assertions / "project_progress_expected.csv", dtype=str)

    # set expected RAG columns to Int64 type in line with transformation logic
    expected_project_progress[["Delivery (RAG)", "Spend (RAG)", "Risk (RAG)"]] = expected_project_progress[
        ["Delivery (RAG)", "Spend (RAG)", "Risk (RAG)"]
    ].astype("Int64")

    # fix assertion data
    expected_project_progress["Leading Factor of Delay"] = expected_project_progress["Leading Factor of Delay"].fillna(
        ""
    )
    assert_frame_equal(extracted_project_progress, expected_project_progress)


def test_extract_risk(mock_risk_sheet, mock_project_lookup, mock_programme_lookup):
    """Test risk data extracted as expected."""
    extracted_risk_data = tf.extract_risks(mock_risk_sheet, mock_project_lookup, mock_programme_lookup, round_four=True)
    expected_risk_data = pd.read_csv(resources_assertions / "risks_expected.csv")
    assert_frame_equal(extracted_risk_data, expected_risk_data)

    # check rows that rows with no risk name entered are retained (in contrast to R3 behaviour)
    risk_value_to_keep = mock_risk_sheet.iloc[30, 4]
    assert risk_value_to_keep in set(extracted_risk_data["Short Description"])

    # Check either project id or programme id populated for each row (but not both). Using XOR(^) operator
    project_xor_programme = extracted_risk_data["Project ID"].notnull() ^ extracted_risk_data["Programme ID"].notnull()
    assert project_xor_programme.all()


def test_full_ingest(mock_ingest_full_extract):
    """
    Tests on top-level ingest function for Towns Fund Round 4.

    Test entity relationships etc.
    """

    # test that sheets that map 1:1 with projects:sheet rows have the same unique project id's
    valid_projects_for_extract = set(mock_ingest_full_extract["Project Details"]["Project ID"])
    assert set(mock_ingest_full_extract["Project Progress"]["Project ID"]) == valid_projects_for_extract
    assert set(mock_ingest_full_extract["Funding Comments"]["Project ID"]) == valid_projects_for_extract
    assert set(mock_ingest_full_extract["Funding"]["Project ID"]) == valid_projects_for_extract
    assert set(mock_ingest_full_extract["Private Investments"]["Project ID"]) == valid_projects_for_extract

    # test tables of mixed programme/project only have valid project id's (including NaN rows mapped only to programme)
    valid_projects_for_extract.add(np.nan)
    assert not set(mock_ingest_full_extract["Output_Data"]["Project ID"]) - valid_projects_for_extract
    assert not set(mock_ingest_full_extract["Outcome_Data"]["Project ID"]) - valid_projects_for_extract
    assert not set(mock_ingest_full_extract["RiskRegister"]["Project ID"]) - valid_projects_for_extract

    # test only valid programmes for this extract are in programme-level tables
    valid_programmes_for_extract = {mock_ingest_full_extract["Place Details"]["Programme ID"][0]}
    assert not set(mock_ingest_full_extract["Programme_Ref"]["Programme ID"]) - valid_programmes_for_extract
    assert not set(mock_ingest_full_extract["Project Details"]["Programme ID"]) - valid_programmes_for_extract
    assert not set(mock_ingest_full_extract["Programme Progress"]["Programme ID"]) - valid_programmes_for_extract
    assert not set(mock_ingest_full_extract["Funding Questions"]["Programme ID"]) - valid_programmes_for_extract

    # test tables of mixed programme/project only have valid programme id's (including NaN rows mapped only to project)
    valid_programmes_for_extract.add(np.nan)
    assert not set(mock_ingest_full_extract["Outcome_Data"]["Programme ID"]) - valid_programmes_for_extract
    assert not set(mock_ingest_full_extract["RiskRegister"]["Programme ID"]) - valid_programmes_for_extract


def test_full_ingest_columns(mock_ingest_full_extract):
    """
    Test columns of all dataframes output by top-level ingest function for Towns Fund Round 4 against mappings.

    Specifically checks all column names for each dataframe extracted by the Round 4 TF pipeline against
    it's corresponding DataMapping sub-tuple of INGEST_MAPPINGS (which contains expected column names for each).
    """
    for mapping in INGEST_MAPPINGS:
        extract_columns = set(mock_ingest_full_extract[mapping.worksheet_name].columns)
        mapping_columns = set(mapping.columns.keys())
        # Submission ID discarded from expected results, as this added later.
        mapping_columns.discard("Submission ID")
        assert mapping_columns == extract_columns
