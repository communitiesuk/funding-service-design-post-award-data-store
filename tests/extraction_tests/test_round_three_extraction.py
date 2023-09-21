"""Tests for Towns Fund Round 3 spreadsheet ingest methods."""
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
from pandas import Timestamp
from pandas.testing import assert_frame_equal

from core.const import OUTCOME_CATEGORIES, OUTPUT_CATEGORIES
from core.controllers.mappings import INGEST_MAPPINGS
from core.exceptions import ValidationError
from core.extraction import towns_fund_round_three as tf
from core.extraction.towns_fund_round_two import ingest_round_two_data_towns_fund

resources = Path(__file__).parent / "resources"
resources_mocks = resources / "mock_sheet_data" / "round_three"
resources_assertions = resources / "assertion_data" / "round_three"


def test_submission_extract():
    """Test that all potential inputs for "Reporting Period" are extracted as expected."""

    # all the potential/possible inputs from ingest form
    test_periods = [
        "2019/20 to 31 March 2022",
        "1 April 2022 to 30 September 2022",
        "1 October 2022 to 31 March 2023",
        "1 April 2023 to 30 September 2023",
        "1 October 2023 to 31 March 2024",
        "1 April 2024 to 30 September 2024",
        "1 October 2024 to 31 March 2025",
        "1 April 2025 to 30 September 2025",
        "1 October 2025 to 31 March 2026",
    ]
    test_df = pd.DataFrame()

    for period in test_periods:
        test_df = pd.concat([test_df, tf.extract_submission_details(period)])
    test_df.reset_index(drop=True, inplace=True)

    test_output = test_df.to_dict(orient="list")
    assert test_output["Reporting Period Start"] == [
        Timestamp("2019-04-01 00:00:00"),
        Timestamp("2022-04-01 00:00:00"),
        Timestamp("2022-10-01 00:00:00"),
        Timestamp("2023-04-01 00:00:00"),
        Timestamp("2023-10-01 00:00:00"),
        Timestamp("2024-04-01 00:00:00"),
        Timestamp("2024-10-01 00:00:00"),
        Timestamp("2025-04-01 00:00:00"),
        Timestamp("2025-10-01 00:00:00"),
    ]

    assert test_output["Reporting Period End"] == [
        Timestamp("2022-03-31 00:00:00"),
        Timestamp("2022-09-30 00:00:00"),
        Timestamp("2023-03-31 00:00:00"),
        Timestamp("2023-09-30 00:00:00"),
        Timestamp("2024-03-31 00:00:00"),
        Timestamp("2024-09-30 00:00:00"),
        Timestamp("2025-03-31 00:00:00"),
        Timestamp("2025-09-30 00:00:00"),
        Timestamp("2026-03-31 00:00:00"),
    ]


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

    Set up a fake dict of dataframes that mimics the Towns Fund V3.0 Excel sheet ingested directly into Pandas.
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

    return tf.ingest_round_three_data_towns_fund(mock_ingest_full_sheet)


def test_place_extract(mock_place_extract):
    """Test extract_place_details simple extraction."""

    extracted_place_df = mock_place_extract
    expected_place_df = pd.read_csv(resources_assertions / "place_details_expected.csv")
    assert_frame_equal(extracted_place_df, expected_place_df)


def test_project_lookup(mock_place_extract):
    """
    Test project lookup table is created as expected.

    Test with both town deal and future high street code lookups.
    """
    # test with Towns Fund
    test_project_identifiers = pd.read_csv(resources_mocks / "project_identifiers_mock.csv")
    test_vals_town_deal = tf.extract_project_lookup(test_project_identifiers, mock_place_extract)
    assert test_vals_town_deal == {
        "Test Project 1": "TD-FAK-01",
        "Test Project 2": "TD-FAK-02",
        "Test Project 3": "TD-FAK-03",
    }

    # test with Future high street (extend fixture data)
    mock_place_extract.Answer[0] = "Future_High_Street_Fund"
    test_vals_future_high_street = tf.extract_project_lookup(test_project_identifiers, mock_place_extract)
    assert test_vals_future_high_street == {
        "Test Project 1": "HS-FAK-01",
        "Test Project 2": "HS-FAK-02",
        "Test Project 3": "HS-FAK-03",
    }


@patch("core.extraction.towns_fund_round_three.TF_PLACE_NAMES_TO_ORGANISATIONS", {"Fake Town": "Fake Canonical Org"})
def test_extract_programme(mock_place_extract, mock_programme_lookup):
    """Test programme info extracted as expected."""
    test_extracted_programme_df = tf.extract_programme(mock_place_extract, mock_programme_lookup)
    expected_programme_df = pd.read_csv(resources_assertions / "programme_ref_expected.csv")
    assert_frame_equal(test_extracted_programme_df, expected_programme_df)


@patch("core.extraction.towns_fund_round_three.TF_PLACE_NAMES_TO_ORGANISATIONS", {"Fake Town": "Fake Canonical Org"})
def test_extract_organisation(mock_place_extract):
    """Test organisations details extracted as expected."""
    test_extracted_organisation_df = tf.extract_organisation(mock_place_extract)
    expected_org_df = pd.read_csv(resources_assertions / "organisation_ref_expected.csv")
    assert_frame_equal(test_extracted_organisation_df, expected_org_df)


def test_extract_projects(mock_project_lookup, mock_programme_lookup):
    """Test projects extracted as expected."""
    mock_project_admin_tab = pd.read_csv(resources_mocks / "project_admin_sheet_mock.csv")
    test_extracted_projects_df = tf.extract_project(mock_project_admin_tab, mock_project_lookup, mock_programme_lookup)
    expected_project_details_df = pd.read_csv(resources_assertions / "project_details_expected.csv")
    assert_frame_equal(test_extracted_projects_df, expected_project_details_df)


def test_extract_programme_progress(mock_progress_sheet, mock_programme_lookup):
    """Test programme progress rows extracted as expected."""
    extracted_programme_progress = tf.extract_programme_progress(mock_progress_sheet, mock_programme_lookup)
    expected_programme_progress = pd.read_csv(resources_assertions / "programme_progress_expected.csv")
    assert_frame_equal(extracted_programme_progress, expected_programme_progress)


def test_extract_project_progress(mock_progress_sheet, mock_project_lookup):
    """Test project progress rows extracted as expected."""

    extracted_project_progress = tf.extract_project_progress(mock_progress_sheet, mock_project_lookup)
    expected_project_progress = pd.read_csv(resources_assertions / "project_progress_expected.csv", dtype=str)

    # set expected RAG columns to Int64 type in line with transformation logic
    expected_project_progress[["Delivery (RAG)", "Spend (RAG)", "Risk (RAG)"]] = expected_project_progress[
        ["Delivery (RAG)", "Spend (RAG)", "Risk (RAG)"]
    ].astype("Int64")

    assert_frame_equal(extracted_project_progress, expected_project_progress)


def test_extract_funding_questions(mock_funding_sheet, mock_programme_lookup):
    """Test programme level funding questions extracted as expected."""
    extracted_funding_questions = tf.extract_funding_questions(mock_funding_sheet, mock_programme_lookup)
    expected_funding_questions = pd.read_csv(resources_assertions / "funding_questions_expected.csv")
    assert_frame_equal(extracted_funding_questions, expected_funding_questions)


def test_extract_funding_questions_fhsf(mock_funding_sheet, mock_programme_lookup):
    """Test programme level funding questions is an empty dataframe when Future High Street Fund is selected."""
    mock_programme_lookup = mock_programme_lookup.replace("TD", "HS")
    extracted_funding_questions = tf.extract_funding_questions(mock_funding_sheet, mock_programme_lookup)
    assert len(extracted_funding_questions.index) == 0
    assert list(extracted_funding_questions.columns) == [
        "Question",
        "Guidance Notes",
        "Indicator",
        "Response",
        "Programme ID",
    ]


def test_extract_funding_comments(mock_funding_sheet, mock_project_lookup):
    """Test project level funding comments extracted as expected."""
    extracted_funding_comments = tf.extract_funding_comments(mock_funding_sheet, mock_project_lookup)
    expected_funding_comments = pd.read_csv(resources_assertions / "funding_comments_expected.csv")
    assert_frame_equal(extracted_funding_comments, expected_funding_comments)


def test_extract_funding_data(mock_funding_sheet, mock_project_lookup):
    """Test project level funding data extracted as expected."""
    extracted_funding_data = tf.extract_funding_data(mock_funding_sheet, mock_project_lookup)
    expected_funding_data = pd.read_csv(resources_assertions / "funding_data_expected.csv", dtype=str)
    # convert to datetime - datetime object serialization slightly different in csv parsing vs Excel.
    expected_funding_data["Start_Date"] = pd.to_datetime(expected_funding_data["Start_Date"], format="%d/%m/%Y")
    expected_funding_data["End_Date"] = pd.to_datetime(expected_funding_data["End_Date"], format="%d/%m/%Y")
    assert_frame_equal(extracted_funding_data, expected_funding_data)


def test_extract_funding_data_programme_only(mock_funding_sheet, mock_project_lookup):
    """Test project level funding data extract does not include excluded data when programme only is selected"""
    mock_funding_sheet.iloc[17, 4] = "Programme only"
    extracted_funding_data = tf.extract_funding_data(mock_funding_sheet, mock_project_lookup)
    assert len(extracted_funding_data.index) == 200
    assert not extracted_funding_data["Funding Source Name"].isin(["Town Deals 5% CDEL Pre-Payment"]).any()


def test_extract_funding_data_fhsf(mock_funding_sheet, mock_project_lookup):
    """Test project level funding data extract does not include excluded questions or excluded forecast. when
    Future_High_Street_Fund is selected"""
    mock_project_lookup = {key: value.replace("TD", "HS") for (key, value) in mock_project_lookup.items()}
    extracted_funding_data = tf.extract_funding_data(mock_funding_sheet, mock_project_lookup)
    assert len(extracted_funding_data.index) == 104
    assert (
        not extracted_funding_data["Funding Source Name"]
        .isin(
            [
                "Town Deals 5% CDEL Pre-Payment",
                "Towns Fund RDEL Payment which is being utilised on TF project related activity",
                "How much of your RDEL forecast is contractually committed?",
            ]
        )
        .any()
    )
    assert (
        len(
            extracted_funding_data[
                (extracted_funding_data["Funding Source Type"] == "Towns Fund")
                & (extracted_funding_data["Start_Date"] > datetime(2023, 10, 1))
            ]
        )
        == 0
    )
    assert (
        len(
            extracted_funding_data[
                (extracted_funding_data["Funding Source Type"] == "Towns Fund")
                & (extracted_funding_data["Start_Date"] <= datetime(2023, 10, 1))
            ]
        )
        == 48
    )


def test_no_extra_projects_in_funding(mock_funding_sheet, mock_project_lookup):
    """
    Check that if extra project sections are filled out in Funding tab, these are ignored.

    Specifically in the case where the "extra" project funding sections are not lsited in the projects listed
    in "project admin" tab.
    """
    test_funding_sheet = mock_funding_sheet.copy()

    # Add an extra project section to Funding tab
    project_name_to_drop = "Mock Project Name"
    test_funding_sheet.iloc[115, 2] = f"Project 4: {project_name_to_drop}"
    extracted_funding_data = tf.extract_funding_data(test_funding_sheet, mock_project_lookup)

    # check the extra project has not been included
    output_project_ids = set(extracted_funding_data["Project ID"].unique())
    extra_projects = output_project_ids - set(mock_project_lookup.values())
    assert not extra_projects


def test_extract_psi(mock_psi_sheet, mock_project_lookup):
    """Test PSI data extracted as expected."""
    extracted_psi = tf.extract_psi(mock_psi_sheet, mock_project_lookup)
    expected_psi = pd.read_csv(resources_assertions / "psi_expected.csv", dtype=str)

    assert_frame_equal(extracted_psi, expected_psi)


def test_extract_outputs(mock_outputs_sheet, mock_project_lookup):
    """Test Outputs data and outputs ref extracted as expected."""
    extracted_output_data = tf.extract_outputs(mock_outputs_sheet, mock_project_lookup)
    expected_output_data = pd.read_csv(resources_assertions / "outputs_data_expected.csv", dtype=str)

    # convert to datetime - datetime object serialization slightly different in csv parsing vs Excel.
    expected_output_data["Start_Date"] = pd.to_datetime(expected_output_data["Start_Date"])
    expected_output_data["End_Date"] = pd.to_datetime(expected_output_data["End_Date"])

    assert_frame_equal(extracted_output_data, expected_output_data)

    # test ref table / categories extracted as expected
    extracted_output_ref = tf.extract_output_categories(extracted_output_data)
    expected_output_ref = pd.read_csv(resources_assertions / "outputs_ref_expected.csv")

    assert_frame_equal(extracted_output_ref, expected_output_ref)

    # test the only category that hasn't come from OUTPUT_CATEGORIES is "custom"
    assert set(extracted_output_ref["Output Category"]) - set(OUTPUT_CATEGORIES.values()) == {"Custom"}
    # test that only outputs from outputs_data are in outputs_ref and vice-versa
    assert set(extracted_output_data["Output"]) == set(extracted_output_ref["Output Name"])


def test_extract_outcomes(mock_outcomes_sheet, mock_project_lookup, mock_programme_lookup):
    """Test Outcome data and outcome ref extracted as expected."""
    extracted_outcome_data = tf.combine_outcomes(mock_outcomes_sheet, mock_project_lookup, mock_programme_lookup)
    expected_outcome_data = pd.read_csv(resources_assertions / "outcomes_data_expected.csv", dtype=str)

    # convert to datetime - datetime object serialization slightly different in csv parsing vs Excel.
    expected_outcome_data["Start_Date"] = pd.to_datetime(expected_outcome_data["Start_Date"])
    expected_outcome_data["End_Date"] = pd.to_datetime(expected_outcome_data["End_Date"])

    assert_frame_equal(extracted_outcome_data, expected_outcome_data)

    # test ref table / categories extracted as expected
    extracted_outcome_ref = tf.extract_outcome_categories(extracted_outcome_data)
    expected_outcome_ref = pd.read_csv(resources_assertions / "outcomes_ref_expected.csv")

    assert_frame_equal(extracted_outcome_ref, expected_outcome_ref)

    # test the only category that hasn't come from OUTCOME_CATEGORIES is "Custom"
    assert set(extracted_outcome_ref["Outcome_Category"]) - set(OUTCOME_CATEGORIES.values()) == {"Custom"}
    # test that only outcome from outcomes_data are in outcomes_ref and vice-versa
    assert set(extracted_outcome_data["Outcome"]) == set(extracted_outcome_ref["Outcome_Name"])

    # check that manually overwritten footfall outcomes are defaulted to normal footfall in extract
    invalid_footfall_outcome = mock_outcomes_sheet.iloc[90, 1]
    assert invalid_footfall_outcome == "test name - overwritten"
    assert invalid_footfall_outcome not in extracted_outcome_data["Outcome"]

    # Check either project id or programme id populated for each row (but not both). Using XOR(^) operator
    project_xor_programme = (
        extracted_outcome_data["Project ID"].notnull() ^ extracted_outcome_data["Programme ID"].notnull()
    )
    assert project_xor_programme.all()


def test_extract_outcomes_with_invalid_project(mock_outcomes_sheet, mock_project_lookup, mock_programme_lookup):
    """Test that appropriate validation error is raised when a project is not present in lookup."""
    # delete project lookup to render project in outcomes to be invalid
    del mock_project_lookup["Test Project 1"]
    with pytest.raises(ValidationError) as ve:
        tf.extract_outcomes(mock_outcomes_sheet, mock_project_lookup, mock_programme_lookup, 3)
    assert str(ve.value) == (
        "[InvalidOutcomeProjectFailure(invalid_project='Test Project 1', section='Outcome Indicators (excluding "
        "footfall)')]"
    )

    with pytest.raises(ValidationError) as ve:
        tf.extract_footfall_outcomes(mock_outcomes_sheet, mock_project_lookup, mock_programme_lookup)
    assert str(ve.value) == (
        "[InvalidOutcomeProjectFailure(invalid_project='Test Project 1', section='Footfall Indicator')]"
    )


def test_extract_risk(mock_risk_sheet, mock_project_lookup, mock_programme_lookup):
    """Test risk data extracted as expected."""
    extracted_risk_data = tf.extract_risks(mock_risk_sheet, mock_project_lookup, mock_programme_lookup)
    expected_risk_data = pd.read_csv(resources_assertions / "risks_expected.csv")
    assert_frame_equal(extracted_risk_data, expected_risk_data)

    # check rows with no risk name entered are dropped/not extracted
    risk_value_to_drop = mock_risk_sheet.iloc[30, 4]
    assert risk_value_to_drop not in set(extracted_risk_data["Short Description"])

    # Check either project id or programme id populated for each row (but not both). Using XOR(^) operator
    project_xor_programme = extracted_risk_data["Project ID"].notnull() ^ extracted_risk_data["Programme ID"].notnull()
    assert project_xor_programme.all()


def test_full_ingest(mock_ingest_full_extract):
    """
    Tests on top-level ingest function for Towns Fund Round 3.

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
    Test columns of all dataframes output by top-level ingest function for Towns Fund Round 3 against mappings.

    Specifically checks all column names for each dataframe extracted by the Round 3 TF pipeline against
    it's corresponding DataMapping sub-tuple of INGEST_MAPPINGS (which contains expected column names for each).
    """
    for mapping in INGEST_MAPPINGS:
        extract_columns = set(mock_ingest_full_extract[mapping.worksheet_name].columns)
        mapping_columns = set(mapping.column_mapping.keys())

        # remove round 4 specific columns
        if mapping.worksheet_name == "Project Progress":
            mapping_columns.discard("Leading Factor of Delay")
            mapping_columns.discard("Current Project Delivery Stage")

        # Submission ID discarded from expected results, as this added later.
        mapping_columns.discard("Submission ID")
        assert mapping_columns == extract_columns


# Test intended only as a local debug tool
@pytest.mark.skip(reason="currently this is just a pytest/pycharm debug entrypoint for ingest work")
def test_ingest_towns_fund_template():
    towns_fund_data = pd.read_excel(
        "EXAMPLE_TF_Reporting_Template_-_TD_-_Newhaven_-_DDMMYY.xlsx",
        sheet_name=None,  # extract from all sheets
    )
    tf.ingest_round_three_data_towns_fund(towns_fund_data)


# Test intended only as a local debug tool
@pytest.mark.skip(reason="currently this is just a pytest/pycharm debug entrypoint for ingest work")
def test_ingest_round_two_historical():
    # TODO: currently testing with small subset of data (to allow reasonable debugging speed)
    round_two_data = pd.read_excel(
        "Round 2 Reporting - Consolidation (MASTER).xlsx",
        # "Round 2 Reporting - Consolidation.xlsx",
        sheet_name=None,  # extract from all sheets
    )
    ingest_round_two_data_towns_fund(round_two_data)
