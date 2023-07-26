"""Tests for Towns Fund Round 3 spreadsheet ingest methods."""
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest
from pandas import Timestamp
from pandas.testing import assert_frame_equal

# isort: off
from core.extraction.towns_fund import (
    extract_submission_details,
    ingest_towns_fund_data,
    extract_place_details,
    extract_project_lookup,
    get_programme_id,
    extract_programme,
    extract_organisation,
    extract_project,
)
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
        test_df = test_df.append(extract_submission_details(period))
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

    return extract_place_details(test_place)


@pytest.fixture
def mock_project_lookup(mock_place_extract):
    """Setup mock project lookup table"""
    test_project_identifiers = pd.read_csv(resources_mocks / "project_identifiers_mock.csv")

    return extract_project_lookup(test_project_identifiers, mock_place_extract)


@pytest.fixture
def mock_programme_lookup(mock_place_extract):
    """Setup mock programme lookup value."""
    test_programme_identifiers = pd.read_csv(resources_mocks / "place_identifiers_mock.csv")
    test_programme = get_programme_id(test_programme_identifiers, mock_place_extract)
    assert test_programme == "TD-FAK"
    return test_programme


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
    test_vals_town_deal = extract_project_lookup(test_project_identifiers, mock_place_extract)
    assert test_vals_town_deal == {
        "Test Project 1": "TD-FAK-01",
        "Test Project 2": "TD-FAK-02",
        "Test Project 3": "TD-FAK-03",
    }

    # test with Future high street (extend fixture data)
    mock_place_extract.Answer[0] = "Future_High_Street_Fund"
    test_vals_future_high_street = extract_project_lookup(test_project_identifiers, mock_place_extract)
    assert test_vals_future_high_street == {
        "Test Project 1": "HS-FAK-01",
        "Test Project 2": "HS-FAK-01",
        "Test Project 3": "HS-FAK-01",
    }


@patch("core.extraction.towns_fund.TF_PLACE_NAMES_TO_ORGANISATIONS", {"Fake Town": "Fake Canonical Org"})
def test_extract_programme(mock_place_extract, mock_programme_lookup):
    """Test programme info extracted as expected."""
    test_extracted_programme_df = extract_programme(mock_place_extract, mock_programme_lookup)
    expected_programme_df = pd.read_csv(resources_assertions / "programme_ref_expected.csv")
    assert_frame_equal(test_extracted_programme_df, expected_programme_df)


@patch("core.extraction.towns_fund.TF_PLACE_NAMES_TO_ORGANISATIONS", {"Fake Town": "Fake Canonical Org"})
def test_extract_organisation(mock_place_extract):
    """Test organisations details extracted as expected."""
    test_extracted_organisation_df = extract_organisation(mock_place_extract)
    expected_org_df = pd.read_csv(resources_assertions / "organisation_ref_expected.csv")
    assert_frame_equal(test_extracted_organisation_df, expected_org_df)


def test_extract_projects(mock_project_lookup, mock_programme_lookup):
    """Test projects extracted as expected."""
    mock_project_admin_tab = pd.read_csv(resources_mocks / "project_admin_sheet_mock.csv")
    test_extracted_projects_df = extract_project(mock_project_admin_tab, mock_project_lookup, mock_programme_lookup)
    expected_project_details_df = pd.read_csv(resources_assertions / "project_details_expected.csv")
    assert_frame_equal(test_extracted_projects_df, expected_project_details_df)


# TODO: Add test of whole extract, and run some assertions ie that projects line up as expected between tabs etc.


# Test intended only as a local debug tool
@pytest.mark.skip(reason="currently this is just a pytest/pycharm debug entrypoint for ingest work")
def test_ingest_towns_fund_template():
    towns_fund_data = pd.read_excel(
        "EXAMPLE_TF_Reporting_Template_-_TD_-_Newhaven_-_DDMMYY.xlsx",
        sheet_name=None,  # extract from all sheets
    )
    ingest_towns_fund_data(towns_fund_data)


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
