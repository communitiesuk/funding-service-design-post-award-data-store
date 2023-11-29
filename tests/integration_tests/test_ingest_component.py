import json
from pathlib import Path
from typing import BinaryIO

import pytest


@pytest.fixture(scope="function")
def towns_fund_round_4_file_success() -> BinaryIO:
    """An example spreadsheet for reporting round 4 of Towns Fund that should ingest without validation errors."""
    with open(Path(__file__).parent / "../resources" / "TF_Round_4_Success.xlsx", "rb") as file:
        yield file


@pytest.fixture(scope="function")
def towns_fund_round_4_file_corrupt() -> BinaryIO:
    """An example spreadsheet for reporting round 4 of Towns Fund that should raise an uknown ingestion error.

    NOTE: File is missing a whole column from the Project Admin sheet.
    """
    with open(Path(__file__).parent / "../resources" / "TF_Round_4_Corrupt.xlsx", "rb") as file:
        yield file


@pytest.fixture(scope="function")
def towns_fund_round_4_file_pre_transformation_failure() -> BinaryIO:
    """An example spreadsheet for reporting round 4 of Towns Fund that should raise pre-transformation failures"""
    with open(Path(__file__).parent / "../resources" / "TF_Round_4_Pre_Transformation_Failure.xlsx", "rb") as file:
        yield file


@pytest.fixture(scope="function")
def towns_fund_round_4_file_project_outcome_failure() -> BinaryIO:
    """An example spreadsheet for reporting round 4 of Towns Fund that should raise an authorisation failure"""
    with open(Path(__file__).parent / "../resources" / "TF_Round_4_Project_Outcome_Failure.xlsx", "rb") as file:
        yield file


@pytest.fixture(scope="function")
def towns_fund_round_4_file_psi_risk_register_failure() -> BinaryIO:
    """An example spreadsheet for reporting round 4 of Towns Fund that should raise TF R4 specific failures"""
    with open(Path(__file__).parent / "../resources" / "TF_Round_4_PSI_RiskRegister_Failure.xlsx", "rb") as file:
        yield file


@pytest.fixture(scope="function")
def towns_fund_round_4_file_project_admin_project_progress_failure() -> BinaryIO:
    """An example spreadsheet for reporting round 4 of Towns Fund that should raise TF R4 specific failures"""
    with open(
        Path(__file__).parent / "../resources" / "TF_Round_4_Project_Admin_Project_Progress_Failure.xlsx", "rb"
    ) as file:
        yield file


@pytest.fixture(scope="function")
def towns_fund_round_4_file_td_funding_failure() -> BinaryIO:
    """An example spreadsheet for reporting round 4 of Towns Fund that should raise TF R4 specific failures"""
    with open(Path(__file__).parent / "../resources" / "TF_Round_4_TD_Funding_Failure.xlsx", "rb") as file:
        yield file


@pytest.fixture(scope="function")
def towns_fund_round_4_file_hs_funding_failure() -> BinaryIO:
    """An example spreadsheet for reporting round 4 of Towns Fund that should raise TF R4 specific failures"""
    with open(Path(__file__).parent / "../resources" / "TF_Round_4_HS_Funding_Failure.xlsx", "rb") as file:
        yield file


@pytest.fixture(scope="function")
def towns_fund_round_4_round_agnostic_failures() -> BinaryIO:
    """An example spreadsheet for reporting round 4 of Towns Fund that should raise TF round agnostic failures"""
    with open(Path(__file__).parent / "../resources" / "TF_Round_4_Round_Agnostic_Failures.xlsx", "rb") as file:
        yield file


def test_ingest_with_r3_file_success(test_client, towns_fund_round_3_file_success):
    """Tests that, given valid inputs, the endpoint responds successfully."""
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": towns_fund_round_3_file_success,
            "reporting_round": 3,
            "do_load": False,
        },
    )

    assert response.status_code == 200, f"{response.json}"
    assert response.json == {
        "detail": "Spreadsheet successfully validated but NOT ingested",
        "loaded": False,
        "metadata": {
            "FundType_ID": "HS",
            "Organisation": "Swindon Borough Council",
            "Programme ID": "HS-SWI",
            "Programme Name": "Swindon",
        },
        "status": 200,
        "title": "success",
    }


def test_ingest_with_r4_file_success_with_load(test_client, towns_fund_round_4_file_success):
    """Tests that, given valid inputs, the endpoint responds successfully."""
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": towns_fund_round_4_file_success,
            "reporting_round": 4,
            "auth": json.dumps(
                {
                    "Place Names": ["Blackfriars - Northern City Centre"],
                    "Fund Types": ["Town_Deal", "Future_High_Street_Fund"],
                }
            ),
            "do_load": True,
        },
    )

    assert response.status_code == 200, f"{response.json}"
    assert response.json == {
        "detail": "Spreadsheet successfully validated and ingested",
        "loaded": True,
        "metadata": {
            "FundType_ID": "HS",
            "Organisation": "Worcester City Council",
            "Programme ID": "HS-WRC",
            "Programme Name": "Blackfriars - Northern City Centre",
        },
        "status": 200,
        "title": "success",
    }


def test_ingest_with_r4_corrupt_submission(test_client, towns_fund_round_4_file_corrupt):
    """Tests that, given a corrupt submission that raises an unhandled exception, the endpoint responds with a 500
    response with an ID field.
    """
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": towns_fund_round_4_file_corrupt,
            "reporting_round": 4,
            "auth": json.dumps(
                {
                    "Place Names": ["Blackfriars - Northern City Centre"],
                    "Fund Types": ["Town_Deal", "Future_High_Street_Fund"],
                }
            ),
        },
    )

    assert response.status_code == 500, f"{response.json}"
    assert response.json["detail"] == "Uncaught ingest exception."
    assert "id" in response.json


def test_ingest_with_r4_file_pre_transformation_failure(
    test_client, towns_fund_round_4_file_pre_transformation_failure
):
    """Tests a TF Round 4 file with PreTransformationFailures on the following:

    - reporting_round
    - form_version
    - place_name
    - fund_type"""
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": towns_fund_round_4_file_pre_transformation_failure,
            "reporting_round": 4,
            "auth": json.dumps(
                {
                    "Place Names": ["Blackfriars - Northern City Centre"],
                    "Fund Types": ["Town_Deal", "Future_High_Street_Fund"],
                }
            ),
            "do_load": False,
        },
    )

    assert response.status_code == 400
    assert response.json == {
        "detail": "Workbook validation failed",
        "pre_transformation_errors": [
            "The selected file must be the Town Deals and Future High Streets Fund Reporting " "Template (v4.3).",
            "Cell B6 in the “start here” tab must say “1 April 2023 to 30 September 2023”. "
            "Select this option from the dropdown list provided.",
            "Cell E7 in the “project admin” must contain a fund type from the dropdown list "
            "provided. Do not enter your own content.",
            "Cell E8 in the “project admin” must contain a place name from the dropdown list "
            "provided. Do not enter your own content.",
        ],
        "status": 400,
        "title": "Bad Request",
        "validation_errors": [],
    }


def test_ingest_with_r4_file_authorisation_failure(test_client, towns_fund_round_4_file_success):
    """Tests TF Round 4 file for which there is an authorisation mismatch between the place_names & fund_types in the
    payload and in the submitted file."""
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": towns_fund_round_4_file_success,
            "reporting_round": 4,
            "auth": json.dumps({"Place Names": ["Rotherham"], "Fund Types": ["Town_Deal"]}),
            "do_load": False,
        },
    )

    assert response.status_code == 400
    assert response.json == {
        "detail": "Workbook validation failed",
        "pre_transformation_errors": [
            "You’re not authorised to submit for Future_High_Street_Fund. You can only submit for Town_Deal.",
            "You’re not authorised to submit for Blackfriars - Northern City Centre. "
            "You can only submit for Rotherham.",
        ],
        "status": 400,
        "title": "Bad Request",
        "validation_errors": [],
    }


def test_ingest_with_r4_file_project_outcome_failure(test_client, towns_fund_round_4_file_project_outcome_failure):
    """Tests a TF Round 4 file with invalid projects in the Outcomes tab raises a
    GenericFailure during transformation."""
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": towns_fund_round_4_file_project_outcome_failure,
            "reporting_round": 4,
            "auth": json.dumps(
                {
                    "Place Names": ["Blackfriars - Northern City Centre"],
                    "Fund Types": ["Town_Deal", "Future_High_Street_Fund"],
                }
            ),
            "do_load": False,
        },
    )

    assert response.status_code == 400
    assert response.json == {
        "detail": "Workbook validation failed",
        "pre_transformation_errors": [],
        "status": 400,
        "title": "Bad Request",
        "validation_errors": [
            {
                "cell_index": "D25",
                "description": "You’ve entered your own content, instead of "
                "selecting from the dropdown list provided. Select "
                "an option from the dropdown list.",
                "error_type": "GenericFailure",
                "section": "Outcome Indicators (excluding footfall)",
                "sheet": "Outcomes",
            }
        ],
    }


def test_ingest_with_r4_file_psi_risk_register_failure(test_client, towns_fund_round_4_file_psi_risk_register_failure):
    """Tests a TF Round 4 file with expected validation errors in PSI, RiskRegister, and Review &
    Sign-Off.

    Expects to raise errors in the following functions:
    - validate_programme_risks
    - validate_project_risks
    - validate_psi_funding_gap
    - validate_psi_funding_not_negative
    - validate_sign_off
    """
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": towns_fund_round_4_file_psi_risk_register_failure,
            "reporting_round": 4,
            "auth": json.dumps(
                {
                    "Place Names": ["Blackfriars - Northern City Centre"],
                    "Fund Types": ["Town_Deal", "Future_High_Street_Fund"],
                }
            ),
            "do_load": False,
        },
    )

    assert response.status_code == 400
    assert response.json == {
        "detail": "Workbook validation failed",
        "pre_transformation_errors": [],
        "status": 400,
        "title": "Bad Request",
        "validation_errors": [
            {
                "cell_index": "H14",
                "description": "You’ve entered a negative number. Enter a positive number.",
                "error_type": "TownsFundRoundFourValidationFailure",
                "section": "Private Sector Investment",
                "sheet": "PSI",
            },
            {
                "cell_index": "J14",
                "description": "The cell is blank but is required. Enter why the "
                "private sector investment gap is greater than "
                "zero.",
                "error_type": "TownsFundRoundFourValidationFailure",
                "section": "Private Sector Investment",
                "sheet": "PSI",
            },
            {
                "cell_index": "C8",
                "description": "The cell is blank but is required.",
                "error_type": "GenericFailure",
                "section": "-",
                "sheet": "Review & Sign-Off",
            },
            {
                "cell_index": "C10",
                "description": "You’ve not entered any programme level risks. You must enter at least 1.",
                "error_type": "TownsFundRoundFourValidationFailure",
                "section": "Programme Risks",
                "sheet": "Risk Register",
            },
            {
                "cell_index": "C21",
                "description": "You’ve not entered any risks for this project. You must enter at least 1.",
                "error_type": "TownsFundRoundFourValidationFailure",
                "section": "Project Risks - Project 1",
                "sheet": "Risk Register",
            },
        ],
    }


def test_ingest_with_r4_file_project_admin_project_progress_failure(
    test_client, towns_fund_round_4_file_project_admin_project_progress_failure
):
    """Tests a TF Round 4 file with expected validation errors in Project Admin & Project Progress.

    Expects to raise errors in the following functions:
    - validate_postcodes
    - validate_project_progress
    - validate_locations
    """
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": towns_fund_round_4_file_project_admin_project_progress_failure,
            "reporting_round": 4,
            "auth": json.dumps(
                {
                    "Place Names": ["Blackfriars - Northern City Centre"],
                    "Fund Types": ["Town_Deal", "Future_High_Street_Fund"],
                }
            ),
            "do_load": False,
        },
    )

    assert response.status_code == 400
    assert response.json == {
        "detail": "Workbook validation failed",
        "pre_transformation_errors": [],
        "status": 400,
        "title": "Bad Request",
        "validation_errors": [
            {
                "cell_index": "F22",
                "description": "The cell is blank but is required for incomplete projects.",
                "error_type": "TownsFundRoundFourValidationFailure",
                "section": "Projects Progress Summary",
                "sheet": "Programme Progress",
            },
            {
                "cell_index": "H31 or K31",
                "description": "You entered an invalid postcode. Enter a full UK postcode, for example SW1A 2AA.",
                "error_type": "TownsFundRoundFourValidationFailure",
                "section": "Project Details",
                "sheet": "Project Admin",
            },
            {
                "cell_index": "J27",
                "description": "The cell is blank but is required.",
                "error_type": "TownsFundRoundFourValidationFailure",
                "section": "Project Details",
                "sheet": "Project Admin",
            },
        ],
    }


def test_ingest_with_r4_file_td_funding_failure(test_client, towns_fund_round_4_file_td_funding_failure):
    """Tests a TF Round 4 file for Town_Deal with expected validation errors in Funding_Profiles.

    Expects to raise errors in the following functions:
    - validate_funding_spent
    - validate_funding_questions
    - validate_funding_profiles_funding_source_enum
    - validate_funding_profiles_funding_secured_not_null
    """
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": towns_fund_round_4_file_td_funding_failure,
            "reporting_round": 4,
            "auth": json.dumps({"Place Names": ["Worcester"], "Fund Types": ["Town_Deal", "Future_High_Street_Fund"]}),
            "do_load": False,
        },
    )

    assert response.status_code == 400
    assert response.json == {
        "detail": "Workbook validation failed",
        "pre_transformation_errors": [],
        "status": 400,
        "title": "Bad Request",
        "validation_errors": [
            {
                "cell_index": "D50",
                "description": "You’ve entered your own content, instead of "
                "selecting from the dropdown list provided. Select "
                "an option from the dropdown list.",
                "error_type": "TownsFundRoundFourValidationFailure",
                "section": "Project Funding Profiles - Project 1",
                "sheet": "Funding Profiles",
            },
            {
                "cell_index": "E50",
                "description": "The cell is blank but is required.",
                "error_type": "TownsFundRoundFourValidationFailure",
                "section": "Project Funding Profiles - Project 1",
                "sheet": "Funding Profiles",
            },
            {
                "cell_index": "Z44",
                "description": "The total RDEL amount is greater than your "
                "allocation. Check the data for each financial "
                "year is correct.",
                "error_type": "TownsFundRoundFourValidationFailure",
                "section": "Project Funding Profiles - Project 1",
                "sheet": "Funding Profiles",
            },
            {
                "cell_index": "Z69",
                "description": "The total CDEL amount is greater than your "
                "allocation. Check the data for each financial "
                "year is correct.",
                "error_type": "TownsFundRoundFourValidationFailure",
                "section": "Project Funding Profiles - Project 2",
                "sheet": "Funding Profiles",
            },
            {
                "cell_index": "E15",
                "description": "The cell is blank but is required.",
                "error_type": "TownsFundRoundFourValidationFailure",
                "section": 'Towns Deal Only - "Other/Early" TD Funding',
                "sheet": "Funding Profiles",
            },
            {
                "cell_index": "F17, F19, I19",
                "description": "You’ve entered your own content, instead of "
                "selecting from the dropdown list provided. Select "
                "an option from the dropdown list.",
                "error_type": "TownsFundRoundFourValidationFailure",
                "section": 'Towns Deal Only - "Other/Early" TD Funding',
                "sheet": "Funding Profiles",
            },
        ],
    }


def test_ingest_with_r4_file_hs_file_failure(test_client, towns_fund_round_4_file_hs_funding_failure):
    """Tests a TF Round 4 file for FHSF with expected validation errors in Funding_Profiles.

    Expects to raise errors in the following functions:
    - validate_funding_profiles_at_least_one_other_funding_source_fhsf
    """
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": towns_fund_round_4_file_hs_funding_failure,
            "reporting_round": 4,
            "auth": json.dumps(
                {
                    "Place Names": ["Blackfriars - Northern City Centre"],
                    "Fund Types": ["Town_Deal", "Future_High_Street_Fund"],
                }
            ),
            "do_load": False,
        },
    )

    assert response.status_code == 400
    assert response.json == {
        "detail": "Workbook validation failed",
        "pre_transformation_errors": [],
        "status": 400,
        "title": "Bad Request",
        "validation_errors": [
            {
                "cell_index": "DNone",
                "description": "You’ve not entered any Other Funding Sources. You "
                "must enter at least 1 over all projects.",
                "error_type": "TownsFundRoundFourValidationFailure",
                "section": "Project Funding Profiles",
                "sheet": "Funding Profiles",
            }
        ],
    }


def test_ingest_with_r4_round_agnostic_failures(test_client, towns_fund_round_4_round_agnostic_failures):
    """Tests a TF Round 4 file raises errors agnostic to a specific round.

    Expects to raise the following errors:
    - WrongTypeFailure
    - NonUniqueCompositeKeyFailure
    - InvalidEnumValueFailure
    - NonNullableConstraintFailure
    """
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": towns_fund_round_4_round_agnostic_failures,
            "reporting_round": 4,
            "auth": json.dumps(
                {
                    "Place Names": ["Blackfriars - Northern City Centre"],
                    "Fund Types": ["Town_Deal", "Future_High_Street_Fund"],
                }
            ),
            "do_load": False,
        },
    )

    assert response.status_code == 400
    assert response.json == {
        "detail": "Workbook validation failed",
        "pre_transformation_errors": [],
        "status": 400,
        "title": "Bad Request",
        "validation_errors": [
            {
                "cell_index": "E22",
                "description": "You’ve entered your own content, instead of "
                "selecting from the dropdown list provided. Select "
                "an option from the dropdown list.",
                "error_type": "InvalidEnumValueFailure",
                "section": "Outcome Indicators (excluding footfall)",
                "sheet": "Outcomes",
            },
            {
                "cell_index": "E25 to W25",
                "description": "The cell is blank but is required. Enter a value, even if it’s zero.",
                "error_type": "NonNullableConstraintFailure",
                "section": "Project Outputs",
                "sheet": "Project Outputs",
            },
            {
                "cell_index": "E63 to W63",
                "description": "You entered text instead of a number. Remove any "
                "units of measurement and only use numbers, "
                "for example, 9.",
                "error_type": "WrongTypeFailure",
                "section": "Project Outputs",
                "sheet": "Project Outputs",
            },
            {
                "cell_index": "C13",
                "description": "You entered duplicate data. Remove or replace the duplicate data.",
                "error_type": "NonUniqueCompositeKeyFailure",
                "section": "Programme Risks",
                "sheet": "Risk Register",
            },
        ],
    }


def test_ingest_endpoint_missing_file(test_client):
    """Tests that, if no excel_file is present, the endpoint returns a 400 error."""
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={},  # empty body
    )

    assert response.status_code == 400
    assert response.json == {
        "detail": "'excel_file' is a required property",
        "status": 400,
        "title": "Bad Request",
        "type": "about:blank",
    }


def test_ingest_without_a_reporting_round(test_client, towns_fund_round_3_file_success):
    """Tests that, given not reporting round, the endpoint returns a 500 error."""
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={"excel_file": towns_fund_round_3_file_success},
    )

    assert response.status_code == 400
    assert response.json == {
        "detail": "'reporting_round' is a required property",
        "status": 400,
        "title": "Bad Request",
        "type": "about:blank",
    }


def test_ingest_with_r4_file_parse_auth_failure(test_client, towns_fund_round_4_file_success):
    """Tests that a TypeError in parse_auth() is aborted with a 400."""
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": towns_fund_round_4_file_success,
            "reporting_round": 4,
            # this auth dict is not a string, therefore will raise a TypeError when json.loads() is called
            "auth": (
                {
                    "Place Names": ["Blackfriars - Northern City Centre"],
                    "Fund Types": ["Town_Deal", "Future_High_Street_Fund"],
                }
            ),
            "do_load": False,
        },
    )

    assert response.status_code == 400
    assert response.json["detail"] == "Invalid auth JSON"
