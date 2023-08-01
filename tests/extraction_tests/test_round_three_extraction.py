"""Tests for Towns Fund Round 3 spreadsheet ingest methods."""
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest
from pandas import Timestamp
from pandas.testing import assert_frame_equal

from core.const import OUTPUT_CATEGORIES
from core.extraction import towns_fund as tf

# isort: off
from core.extraction.towns_fund_round_two import ingest_round_two_data_towns_fund

# isort: on

resources = Path(__file__).parent / "resources"
resources_mocks = resources / "mock_sheet_data"
resources_assertions = resources / "assertion_data"


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
        test_df = test_df.append(tf.extract_submission_details(period))
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
def mock_place_extract():
    """Setup test place sheet extract."""
    test_place = pd.read_csv(resources_mocks / "project_admin_sheet_mock.csv")

    return tf.extract_place_details(test_place)


@pytest.fixture
def mock_project_lookup(mock_place_extract):
    """Setup mock project lookup table"""
    test_project_identifiers = pd.read_csv(resources_mocks / "project_identifiers_mock.csv")

    return tf.extract_project_lookup(test_project_identifiers, mock_place_extract)


@pytest.fixture
def mock_programme_lookup(mock_place_extract):
    """Setup mock programme lookup value."""
    test_programme_identifiers = pd.read_csv(resources_mocks / "place_identifiers_mock.csv")
    test_programme = tf.get_programme_id(test_programme_identifiers, mock_place_extract)
    assert test_programme == "TD-FAK"
    return test_programme


@pytest.fixture
def mock_progress_sheet():
    """Setup mock programme/project progress sheet.

    Ignores time conversions from Excel to Python (lost in process of saving mock data as csv)."""
    test_progress_df = pd.read_csv(resources_mocks / "programme_progress_mock.csv")

    return test_progress_df


@pytest.fixture
def mock_funding_sheet():
    """Load mock funding sheet into dataframe from csv."""
    test_funding_df = pd.read_csv(resources_mocks / "funding_profiles_mock.csv")

    return test_funding_df


@pytest.fixture
def mock_psi_sheet():
    """Load mock private investments sheet into dataframe from csv."""
    test_psi_df = pd.read_csv(resources_mocks / "psi_mock.csv")

    return test_psi_df


@pytest.fixture
def mock_outputs_sheet():
    """Load fake project outputs sheet into dataframe from csv."""
    test_outputs_df = pd.read_csv(resources_mocks / "outputs_mock.csv")

    return test_outputs_df


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
        "Test Project 2": "HS-FAK-01",
        "Test Project 3": "HS-FAK-01",
    }


@patch("core.extraction.towns_fund.TF_PLACE_NAMES_TO_ORGANISATIONS", {"Fake Town": "Fake Canonical Org"})
def test_extract_programme(mock_place_extract, mock_programme_lookup):
    """Test programme info extracted as expected."""
    test_extracted_programme_df = tf.extract_programme(mock_place_extract, mock_programme_lookup)
    expected_programme_df = pd.read_csv(resources_assertions / "programme_ref_expected.csv")
    assert_frame_equal(test_extracted_programme_df, expected_programme_df)


@patch("core.extraction.towns_fund.TF_PLACE_NAMES_TO_ORGANISATIONS", {"Fake Town": "Fake Canonical Org"})
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
    assert_frame_equal(extracted_project_progress, expected_project_progress)


def test_extract_funding_questions(mock_funding_sheet, mock_programme_lookup):
    """Test programme level funding questions extracted as expected."""
    extracted_funding_questions = tf.extract_funding_questions(mock_funding_sheet, mock_programme_lookup)
    expected_funding_questions = pd.read_csv(resources_assertions / "funding_questions_expected.csv")
    assert_frame_equal(extracted_funding_questions, expected_funding_questions)


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


# TODO: Add test of whole extract, and run some assertions ie that projects line up as expected between tabs etc.


# Test intended only as a local debug tool
@pytest.mark.skip(reason="currently this is just a pytest/pycharm debug entrypoint for ingest work")
def test_ingest_towns_fund_template():
    towns_fund_data = pd.read_excel(
        "EXAMPLE_TF_Reporting_Template_-_TD_-_Newhaven_-_DDMMYY.xlsx",
        sheet_name=None,  # extract from all sheets
    )
    tf.ingest_towns_fund_data(towns_fund_data)


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
