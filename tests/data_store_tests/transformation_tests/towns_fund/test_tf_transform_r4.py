"""
Round 4 extraction is almost identical to Round 3 and so re-uses many components.

The tests in this module cover new functionality unique to Round 4.
"""

from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
from pandas._testing import assert_frame_equal

import data_store.transformation.towns_fund.tf_transform_r3 as tf
from data_store.exceptions import OldValidationError
from data_store.transformation.towns_fund.tf_transform_r4 import (
    extract_programme_progress,
    transform,
)

resources = Path(__file__).parent / "resources"
resources_mocks = resources / "mock_sheet_data" / "round_four"
resources_assertions = resources / "assertion_data" / "round_four"


@pytest.fixture(scope="module")
def mock_progress_sheet():
    """Setup mock programme/project progress sheet.

    Ignores time conversions from Excel to Python (lost in process of saving mock data as csv)."""
    test_progress_df = pd.read_csv(resources_mocks / "programme_progress_mock.csv", header=None)

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
@patch(
    "data_store.transformation.towns_fund.tf_transform_r3.TF_PLACE_NAMES_TO_ORGANISATIONS",
    {"Fake Town": "Fake Canonical Org"},
)
def mock_ingest_full_extract(mock_ingest_full_sheet):
    """Setup mock of full spreadsheet extract."""

    return transform(mock_ingest_full_sheet)


def test_extract_programme_progress(mock_progress_sheet, mock_programme_lookup):
    """Test programme progress rows extracted as expected."""
    extracted_programme_progress = extract_programme_progress(mock_progress_sheet, mock_programme_lookup)
    expected_programme_progress = pd.read_csv(resources_assertions / "programme_progress_expected.csv", index_col=0)

    assert_frame_equal(extracted_programme_progress, expected_programme_progress)


def test_extract_project_progress(mock_progress_sheet, mock_project_lookup):
    """Test project progress rows extracted as expected."""
    # round four parameter set to true
    extracted_project_progress = tf.extract_project_progress(mock_progress_sheet, mock_project_lookup, 4)
    expected_project_progress = pd.read_csv(
        resources_assertions / "project_progress_expected.csv", index_col=0, dtype=str
    )

    # fix assertion data
    expected_project_progress["leading_factor_of_delay"] = expected_project_progress["leading_factor_of_delay"].fillna(
        ""
    )

    assert pd.isna(extracted_project_progress["risk_rag"].iloc[0])  # empty cells should be extracted as pd.NA
    assert isinstance(extracted_project_progress["delivery_rag"].iloc[0], str)  # filled cells should be str
    assert isinstance(extracted_project_progress["spend_rag"].iloc[0], str)  # filled cells should be str
    assert_frame_equal(extracted_project_progress, expected_project_progress)


def test_extract_funding_data_fhsf(mock_funding_sheet, mock_project_lookup):
    """Round 4 param for extract_funding_data should retain an extra half of funding data."""
    mock_project_lookup = {key: value.replace("TD", "HS") for (key, value) in mock_project_lookup.items()}
    extracted_funding_data = tf.extract_funding_data(mock_funding_sheet, mock_project_lookup, 4)

    assert (
        len(
            extracted_funding_data[
                (extracted_funding_data["funding_source"] == "Towns Fund")
                & (extracted_funding_data["start_date"] >= datetime(year=2024, month=4, day=1))
            ]
        )
        != 0
    )


def test_extract_risk(mock_risk_sheet, mock_project_lookup, mock_programme_lookup):
    """Test risk data extracted as expected."""
    extracted_risk_data = tf.extract_risks(mock_risk_sheet, mock_project_lookup, mock_programme_lookup, 4)
    expected_risk_data = pd.read_csv(resources_assertions / "risks_expected.csv", index_col=0)
    assert_frame_equal(extracted_risk_data, expected_risk_data)

    # check rows that rows with no risk name entered are retained (in contrast to R3 behaviour)
    risk_value_to_keep = mock_risk_sheet.iloc[30, 4]
    assert risk_value_to_keep in set(extracted_risk_data["short_desc"])

    # Check either project id or programme id populated for each row (but not both). Using XOR(^) operator
    project_xor_programme = extracted_risk_data["project_id"].notnull() ^ extracted_risk_data["programme_id"].notnull()
    assert project_xor_programme.all()


def test_full_ingest(mock_ingest_full_extract):
    """
    Tests on top-level ingest function for Towns Fund Round 4.

    Test entity relationships etc.
    """

    # test that sheets that map 1:1 with projects:sheet rows have the same unique project id's
    valid_projects_for_extract = set(mock_ingest_full_extract["Project Details"]["project_id"])
    assert set(mock_ingest_full_extract["Project Progress"]["project_id"]) == valid_projects_for_extract
    assert set(mock_ingest_full_extract["Funding Comments"]["project_id"]) == valid_projects_for_extract
    assert set(mock_ingest_full_extract["Funding"]["project_id"]) == valid_projects_for_extract
    assert set(mock_ingest_full_extract["Private Investments"]["project_id"]) == valid_projects_for_extract

    # test tables of mixed programme/project only have valid project id's (including NaN rows mapped only to programme)
    valid_projects_for_extract.add(np.nan)
    assert not set(mock_ingest_full_extract["Output_Data"]["project_id"]) - valid_projects_for_extract
    assert not set(mock_ingest_full_extract["Outcome_Data"]["project_id"]) - valid_projects_for_extract
    assert not set(mock_ingest_full_extract["RiskRegister"]["project_id"]) - valid_projects_for_extract

    # test only valid programmes for this extract are in programme-level tables
    valid_programmes_for_extract = {mock_ingest_full_extract["Place Details"]["programme_id"].iloc[0]}
    assert not set(mock_ingest_full_extract["Programme_Ref"]["programme_id"]) - valid_programmes_for_extract
    assert not set(mock_ingest_full_extract["Project Details"]["programme_id"]) - valid_programmes_for_extract
    assert not set(mock_ingest_full_extract["Programme Progress"]["programme_id"]) - valid_programmes_for_extract
    assert not set(mock_ingest_full_extract["Funding Questions"]["programme_id"]) - valid_programmes_for_extract

    # test tables of mixed programme/project only have valid programme id's (including NaN rows mapped only to project)
    valid_programmes_for_extract.add(np.nan)
    assert not set(mock_ingest_full_extract["Outcome_Data"]["programme_id"]) - valid_programmes_for_extract
    assert not set(mock_ingest_full_extract["RiskRegister"]["programme_id"]) - valid_programmes_for_extract


def test_extract_outcomes_with_null_project(mock_outcomes_sheet, mock_project_lookup, mock_programme_lookup):
    """Test that appropriate validation error is raised when a project null."""
    # replace a valid project with a null
    mock_outcomes_sheet = mock_outcomes_sheet.replace("Test Project 1", np.nan)
    with pytest.raises(OldValidationError) as ve:
        tf.extract_outcomes(mock_outcomes_sheet, mock_project_lookup, mock_programme_lookup, 4)
    assert str(ve.value.validation_failures) == (
        "[GenericFailure(table='Outcome_Data', section='Outcome Indicators (excluding footfall)', message='You’ve "
        "entered your own content, instead of selecting from the dropdown list provided. Select an option from "
        "the dropdown list.', cell_index=None, column='Relevant project(s)', row_index=23), GenericFailure("
        "table='Outcome_Data', section='Outcome Indicators (excluding footfall)', message='You’ve entered your "
        "own content, instead of selecting from the dropdown list provided. Select an option from the dropdown "
        "list.', cell_index=None, column='Relevant project(s)', row_index=24), GenericFailure("
        "table='Outcome_Data', section='Outcome Indicators (excluding footfall)', message='You’ve entered your "
        "own content, instead of selecting from the dropdown list provided. Select an option from the dropdown "
        "list.', cell_index=None, column='Relevant project(s)', row_index=43)]"
    )


def test_original_indexes_retained(mock_ingest_full_extract):
    """Test that the original index is retained after transformation.

    After transformation, we expect that the indexes of the DataFrames will match what they were when the file was
    first extracted. This test looks up the first and last indexes, and asserts that they equal the number of the
    indexes for the first and last values of a given DataFrame before transformation.
    """
    assert mock_ingest_full_extract["Project Details"].index[0] == 27
    assert mock_ingest_full_extract["Project Details"].index[-1] == 29
    assert mock_ingest_full_extract["Place Details"].index[0] == 7
    assert mock_ingest_full_extract["Place Details"].index[-1] == 21
    assert mock_ingest_full_extract["Programme Progress"].index[0] == 7
    assert mock_ingest_full_extract["Programme Progress"].index[-1] == 13
    assert mock_ingest_full_extract["Project Progress"].index[0] == 20
    assert mock_ingest_full_extract["Project Progress"].index[-1] == 22
    assert mock_ingest_full_extract["Funding Questions"].index[0] == 15
    assert mock_ingest_full_extract["Funding Questions"].index[-1] == 19
    assert mock_ingest_full_extract["Funding Comments"].index[0] == 59
    assert mock_ingest_full_extract["Funding Comments"].index[-1] == 115
    assert mock_ingest_full_extract["Funding"].index[0] == 40
    assert mock_ingest_full_extract["Funding"].index[-1] == 98
    assert mock_ingest_full_extract["Private Investments"].index[0] == 13
    assert mock_ingest_full_extract["Private Investments"].index[-1] == 15
    assert mock_ingest_full_extract["Output_Data"].index[0] == 24
    assert mock_ingest_full_extract["Output_Data"].index[-1] == 102
    assert mock_ingest_full_extract["Outcome_Data"].index[0] == 23
    assert mock_ingest_full_extract["Outcome_Data"].index[-1] == 92
    assert mock_ingest_full_extract["RiskRegister"].index[0] == 12
    assert mock_ingest_full_extract["RiskRegister"].index[-1] == 32


def test_project_details_indexes(mock_ingest_full_extract):
    """Test that the indexes for Project Details are not lost in transformation."""
    assert mock_ingest_full_extract["Project Details"]["project_name"][27] == "Test Project 1"
    assert mock_ingest_full_extract["Project Details"]["project_name"][28] == "Test Project 2"
    assert mock_ingest_full_extract["Project Details"]["project_name"][29] == "Test Project 3"


def test_place_details_indexes(mock_ingest_full_extract):
    """Test that the indexes for Place Details are not lost in transformation."""
    assert mock_ingest_full_extract["Place Details"]["answer"][7] == "Town_Deal"
    assert mock_ingest_full_extract["Place Details"]["answer"][8] == "Fake Town"
    assert mock_ingest_full_extract["Place Details"]["answer"][9] == "Test Org"


def test_programme_progress_indexes(mock_ingest_full_extract):
    """Test that the indexes for Programme Progress are not lost in transformation."""
    assert mock_ingest_full_extract["Programme Progress"]["answer"][7] == "some comment on profile / forecast"
    assert mock_ingest_full_extract["Programme Progress"]["answer"][8] == "Test comment progress update"
    assert mock_ingest_full_extract["Programme Progress"]["answer"][9] == "Test comment, challenges"


def test_project_progress_indexes(mock_ingest_full_extract):
    """Test that the indexes for Project Progress are not lost in transformation."""
    assert mock_ingest_full_extract["Project Progress"]["project_id"][20] == "TD-FAK-01"
    assert mock_ingest_full_extract["Project Progress"]["project_id"][21] == "TD-FAK-02"
    assert mock_ingest_full_extract["Project Progress"]["project_id"][22] == "TD-FAK-03"


def test_funding_questions_indexes(mock_ingest_full_extract):
    """Test that the indexes for Funding Questions are not lost in transformation."""
    assert mock_ingest_full_extract["Funding Questions"]["question"][15] == (
        "Beyond these three funding types, have " "you received any payments for specific " "projects?"
    )
    assert mock_ingest_full_extract["Funding Questions"]["question"][17].iloc[0] == (
        "Please confirm whether the amount " "utilised represents your entire " "allocation"
    )
    assert mock_ingest_full_extract["Funding Questions"]["question"][20].iloc[0] == (
        "Please explain in detail how the " "funding has, or will be, " "utilised"
    )


def test_funding_comments_indexes(mock_ingest_full_extract):
    """Test that the indexes for Funding Comments are not lost in transformation."""
    assert mock_ingest_full_extract["Funding Comments"]["comment"][59] == "Test comment 1"
    assert mock_ingest_full_extract["Funding Comments"]["comment"][87] == "Test comment 2"
    assert str(mock_ingest_full_extract["Funding Comments"]["comment"][115]) == "nan"


def test_funding_indexes(mock_ingest_full_extract):
    """Test that the indexes for Funding are not lost in transformation."""
    assert mock_ingest_full_extract["Funding"]["funding_source"][52].iloc[0] == "Source 2"
    assert mock_ingest_full_extract["Funding"]["funding_source"][78].iloc[0] == "Test source project 2"
    assert mock_ingest_full_extract["Funding"]["funding_source"][50].iloc[0] == "Test source"


def test_private_investments_indexes(mock_ingest_full_extract):
    """Test that the indexes for Private Investments are not lost in transformation."""
    assert mock_ingest_full_extract["Private Investments"]["project_id"][13] == "TD-FAK-01"
    assert mock_ingest_full_extract["Private Investments"]["project_id"][14] == "TD-FAK-02"
    assert mock_ingest_full_extract["Private Investments"]["project_id"][15] == "TD-FAK-03"


def test_outputs_indexes(mock_ingest_full_extract):
    """Test that the indexes for Outputs are not lost in transformation."""
    assert mock_ingest_full_extract["Output_Data"]["output"][24].iloc[0] == "# of temporary FT jobs supported"
    assert mock_ingest_full_extract["Output_Data"]["output"][25].iloc[0] == (
        "# of full-time equivalent (FTE) permanent " "jobs " "created through the project"
    )
    assert mock_ingest_full_extract["Output_Data"]["output"][26].iloc[0] == (
        "# of full-time equivalent (FTE) permanent " "jobs safeguarded through the project"
    )


def test_outcomes_indexes(mock_ingest_full_extract):
    """Test that the indexes for Outcomes are not lost in transformation."""
    assert mock_ingest_full_extract["Outcome_Data"]["outcome"][23].iloc[0] == (
        "Patronage of the public transport system in " "the area of interest (for public transport " "schemes)"
    )
    assert mock_ingest_full_extract["Outcome_Data"]["outcome"][43].iloc[0] == "test custom outcome"
    assert mock_ingest_full_extract["Outcome_Data"]["outcome"][24].iloc[0] == (
        "Estimated carbon dioxide equivalent reductions as a result of support"
    )
    assert mock_ingest_full_extract["Outcome_Data"]["outcome"][60].iloc[0] == (
        "Year on Year monthly % change in footfall"
    )


def test_risk_indexes(mock_ingest_full_extract):
    """Test that the indexes for Risks are not lost in transformation."""
    assert mock_ingest_full_extract["RiskRegister"]["risk_name"][12] == "test programme risk 1"
    assert mock_ingest_full_extract["RiskRegister"]["risk_name"][23] == "project risk test 1"
    assert mock_ingest_full_extract["RiskRegister"]["risk_name"][24] == "project risk test 2"
