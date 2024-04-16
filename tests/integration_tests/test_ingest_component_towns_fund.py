import json
from pathlib import Path
from typing import BinaryIO

import pytest
from botocore.exceptions import ClientError, EndpointConnectionError

from core.db import db
from core.db.entities import ProgrammeJunction, Project, ProjectProgress, Submission


@pytest.fixture(scope="function")
def towns_fund_round_4_file_success_duplicate() -> BinaryIO:
    """Duplicate of an example spreadsheet for reporting round 4 of Towns Fund that should ingest without validation
    errors."""
    with open(Path(__file__).parent / "mock_tf_returns" / "TF_Round_4_Success_Duplicate.xlsx", "rb") as file:
        yield file


@pytest.fixture(scope="function")
def towns_fund_round_4_file_corrupt() -> BinaryIO:
    """An example spreadsheet for reporting round 4 of Towns Fund that should raise an uknown ingestion error.

    NOTE: File is missing a whole column from the Project Admin sheet.
    """
    with open(Path(__file__).parent / "mock_tf_returns" / "TF_Round_4_Corrupt.xlsx", "rb") as file:
        yield file


@pytest.fixture(scope="function")
def towns_fund_round_4_file_pre_transformation_failure() -> BinaryIO:
    """An example spreadsheet for reporting round 4 of Towns Fund that should raise pre-transformation failures"""
    with open(Path(__file__).parent / "mock_tf_returns" / "TF_Round_4_Pre_Transformation_Failure.xlsx", "rb") as file:
        yield file


@pytest.fixture(scope="function")
def towns_fund_round_4_file_project_outcome_failure() -> BinaryIO:
    """An example spreadsheet for reporting round 4 of Towns Fund that should raise an authorisation failure"""
    with open(Path(__file__).parent / "mock_tf_returns" / "TF_Round_4_Project_Outcome_Failure.xlsx", "rb") as file:
        yield file


@pytest.fixture(scope="function")
def towns_fund_round_4_file_psi_risk_register_failure() -> BinaryIO:
    """An example spreadsheet for reporting round 4 of Towns Fund that should raise TF R4 specific failures"""
    with open(Path(__file__).parent / "mock_tf_returns" / "TF_Round_4_PSI_RiskRegister_Failure.xlsx", "rb") as file:
        yield file


@pytest.fixture(scope="function")
def towns_fund_round_4_file_project_admin_project_progress_failure() -> BinaryIO:
    """An example spreadsheet for reporting round 4 of Towns Fund that should raise TF R4 specific failures"""
    with open(
        Path(__file__).parent / "mock_tf_returns" / "TF_Round_4_Project_Admin_Project_Progress_Failure.xlsx", "rb"
    ) as file:
        yield file


@pytest.fixture(scope="function")
def towns_fund_round_4_file_td_funding_failure() -> BinaryIO:
    """An example spreadsheet for reporting round 4 of Towns Fund that should raise TF R4 specific failures"""
    with open(Path(__file__).parent / "mock_tf_returns" / "TF_Round_4_TD_Funding_Failure.xlsx", "rb") as file:
        yield file


@pytest.fixture(scope="function")
def towns_fund_round_4_file_hs_funding_failure() -> BinaryIO:
    """An example spreadsheet for reporting round 4 of Towns Fund that should raise TF R4 specific failures"""
    with open(Path(__file__).parent / "mock_tf_returns" / "TF_Round_4_HS_Funding_Failure.xlsx", "rb") as file:
        yield file


@pytest.fixture(scope="function")
def wrong_format_test_file() -> BinaryIO:
    """An invalid text test file."""
    with open(Path(__file__).parent / "mock_tf_returns" / "wrong_format_test_file.txt", "rb") as file:
        yield file


@pytest.fixture(scope="function")
def towns_fund_round_3_same_programme_as_round_4_file() -> BinaryIO:
    """Round 3 data with the same programme as in 'TF_Round_4_Success.xlsx'."""
    with open(Path(__file__).parent / "mock_tf_returns" / "TF_Round_3_Same_Prog_As_Round_4.xlsx", "rb") as file:
        yield file


def test_ingest_with_r3_file_success(test_client_reset, towns_fund_round_3_file_success, test_buckets):
    """Tests that, given valid inputs, the endpoint responds successfully."""
    endpoint = "/ingest"
    response = test_client_reset.post(
        endpoint,
        data={
            "excel_file": towns_fund_round_3_file_success,
            "fund_name": "Towns Fund",
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


def test_ingest_with_r4_file_success_with_load(test_client_reset, towns_fund_round_4_file_success, test_buckets):
    """Tests that, given valid inputs, the endpoint responds successfully."""
    endpoint = "/ingest"
    response = test_client_reset.post(
        endpoint,
        data={
            "excel_file": towns_fund_round_4_file_success,
            "fund_name": "Towns Fund",
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


def test_ingest_with_r4_file_success_with_no_auth(test_client_reset, towns_fund_round_4_file_success, test_buckets):
    """Tests that, given valid inputs and no auth params, the endpoint responds successfully."""
    endpoint = "/ingest"
    response = test_client_reset.post(
        endpoint,
        data={
            "excel_file": towns_fund_round_4_file_success,
            "fund_name": "Towns Fund",
            "reporting_round": 4,
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


def test_ingest_with_r4_file_success_with_load_re_ingest(
    test_client_reset, towns_fund_round_4_file_success, towns_fund_round_4_file_success_duplicate, test_buckets
):
    """Tests that, given valid inputs, the endpoint responds successfully when file re-ingested."""
    endpoint = "/ingest"
    test_client_reset.post(
        endpoint,
        data={
            "excel_file": towns_fund_round_4_file_success,
            "fund_name": "Towns Fund",
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

    programme_junction_rows_first_ingest = ProgrammeJunction.query.all()
    programme_id_first_ingest = programme_junction_rows_first_ingest[0].programme_id
    submission_id_first_ingest = programme_junction_rows_first_ingest[0].submission_id
    project_detail_rows_first_ingest = Project.query.all()

    # must commit to end the pending transaction so another can begin
    db.session.commit()

    response = test_client_reset.post(
        endpoint,
        data={
            "excel_file": towns_fund_round_4_file_success_duplicate,
            "fund_name": "Towns Fund",
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

    programme_junction_rows_second_ingest = ProgrammeJunction.query.all()
    programme_id_second_ingest = programme_junction_rows_second_ingest[0].programme_id
    submission_id_second_ingest = programme_junction_rows_second_ingest[0].submission_id
    project_detail_rows_second_ingest = Project.query.all()

    # the number of Programmes, Submissions, and their children should be the same after re-ingest
    assert len(programme_junction_rows_first_ingest) == len(programme_junction_rows_second_ingest)
    assert len(project_detail_rows_first_ingest) == len(project_detail_rows_second_ingest)
    # the Programme ID should remain the same, but the Submission ID should be different
    assert programme_id_first_ingest == programme_id_second_ingest
    assert submission_id_first_ingest != submission_id_second_ingest


def test_ingest_with_r4_corrupt_submission(test_client, towns_fund_round_4_file_corrupt, test_buckets):
    """Tests that, given a corrupt submission that raises an unhandled exception, the endpoint responds with a 500
    response with an ID field.
    """
    # TODO we should also test that the file has been uploaded to failed files S3 bucket
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": towns_fund_round_4_file_corrupt,
            "fund_name": "Towns Fund",
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
    assert "Uncaught ingest exception" in response.json["detail"]
    assert "id" in response.json


def test_ingest_with_r4_file_pre_transformation_failure(
    test_client, towns_fund_round_4_file_pre_transformation_failure, test_buckets
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
            "fund_name": "Towns Fund",
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


def test_ingest_with_r4_file_authorisation_failure(test_client, towns_fund_round_4_file_success, test_buckets):
    """Tests TF Round 4 file for which there is an authorisation mismatch between the place_names & fund_types in the
    payload and in the submitted file."""
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": towns_fund_round_4_file_success,
            "fund_name": "Towns Fund",
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


def test_ingest_with_r4_file_project_outcome_failure(
    test_client, towns_fund_round_4_file_project_outcome_failure, test_buckets
):
    """Tests a TF Round 4 file with invalid projects in the Outcomes tab raises a
    GenericFailure during transformation."""
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": towns_fund_round_4_file_project_outcome_failure,
            "fund_name": "Towns Fund",
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


def test_ingest_with_r4_file_psi_risk_register_failure(
    test_client, towns_fund_round_4_file_psi_risk_register_failure, test_buckets
):
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
            "fund_name": "Towns Fund",
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
                "error_type": "GenericFailure",
                "section": "Private Sector Investment",
                "sheet": "PSI",
            },
            {
                "cell_index": "J14",
                "description": "The cell is blank but is required. Enter why the "
                "private sector investment gap is greater than "
                "zero.",
                "error_type": "GenericFailure",
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
                "error_type": "GenericFailure",
                "section": "Programme Risks",
                "sheet": "Risk Register",
            },
            {
                "cell_index": "C21",
                "description": "You’ve not entered any risks for this project. You must enter at least 1.",
                "error_type": "GenericFailure",
                "section": "Project Risks - Project 1",
                "sheet": "Risk Register",
            },
        ],
    }


def test_ingest_with_r4_file_project_admin_project_progress_failure(
    test_client, towns_fund_round_4_file_project_admin_project_progress_failure, test_buckets
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
            "fund_name": "Towns Fund",
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
                "error_type": "GenericFailure",
                "section": "Projects Progress Summary",
                "sheet": "Programme Progress",
            },
            {
                "cell_index": "H31 or K31",
                "description": "You entered an invalid postcode. Enter a full UK postcode, for example SW1A 2AA.",
                "error_type": "GenericFailure",
                "section": "Project Details",
                "sheet": "Project Admin",
            },
            {
                "cell_index": "J27",
                "description": "The cell is blank but is required.",
                "error_type": "GenericFailure",
                "section": "Project Details",
                "sheet": "Project Admin",
            },
        ],
    }


def test_ingest_with_r4_file_td_funding_failure(test_client, towns_fund_round_4_file_td_funding_failure, test_buckets):
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
            "fund_name": "Towns Fund",
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
                "error_type": "GenericFailure",
                "section": "Project Funding Profiles - Project 1",
                "sheet": "Funding Profiles",
            },
            {
                "cell_index": "E50",
                "description": "The cell is blank but is required.",
                "error_type": "GenericFailure",
                "section": "Project Funding Profiles - Project 1",
                "sheet": "Funding Profiles",
            },
            {
                "cell_index": "Z44",
                "description": "The total RDEL amount is greater than your "
                "allocation. Check the data for each financial "
                "year is correct.",
                "error_type": "GenericFailure",
                "section": "Project Funding Profiles - Project 1",
                "sheet": "Funding Profiles",
            },
            {
                "cell_index": "Z69",
                "description": "The total CDEL amount is greater than your "
                "allocation. Check the data for each financial "
                "year is correct.",
                "error_type": "GenericFailure",
                "section": "Project Funding Profiles - Project 2",
                "sheet": "Funding Profiles",
            },
            {
                "cell_index": "E15",
                "description": "The cell is blank but is required.",
                "error_type": "GenericFailure",
                "section": 'Towns Deal Only - "Other/Early" TD Funding',
                "sheet": "Funding Profiles",
            },
            {
                "cell_index": "F17, F19, I19",
                "description": "You’ve entered your own content, instead of "
                "selecting from the dropdown list provided. Select "
                "an option from the dropdown list.",
                "error_type": "GenericFailure",
                "section": 'Towns Deal Only - "Other/Early" TD Funding',
                "sheet": "Funding Profiles",
            },
        ],
    }


def test_ingest_with_r4_file_hs_file_failure(test_client, towns_fund_round_4_file_hs_funding_failure, test_buckets):
    """Tests a TF Round 4 file for FHSF with expected validation errors in Funding_Profiles.

    Expects to raise errors in the following functions:
    - validate_funding_profiles_at_least_one_other_funding_source_fhsf
    """
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": towns_fund_round_4_file_hs_funding_failure,
            "fund_name": "Towns Fund",
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
                "cell_index": "D",
                "description": "You’ve not entered any Other Funding Sources. You "
                "must enter at least 1 over all projects.",
                "error_type": "GenericFailure",
                "section": "Project Funding Profiles",
                "sheet": "Funding Profiles",
            }
        ],
    }


def test_ingest_with_r4_round_agnostic_failures(test_client, towns_fund_round_4_round_agnostic_failures, test_buckets):
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
            "fund_name": "Towns Fund",
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


def test_ingest_without_a_reporting_round(test_client, towns_fund_round_3_file_success, test_buckets):
    """Tests that, given not reporting round, the endpoint returns a 400 error."""
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={"excel_file": towns_fund_round_3_file_success, "fund_name": "Towns Fund"},
    )

    assert response.status_code == 400
    assert response.json == {
        "detail": "'reporting_round' is a required property",
        "status": 400,
        "title": "Bad Request",
        "type": "about:blank",
    }


def test_ingest_without_a_fund_name(test_client, towns_fund_round_3_file_success, test_buckets):
    """Tests that, given no fund_name, the endpoint returns a 400 error."""
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={"excel_file": towns_fund_round_3_file_success, "reporting_round": 4},
    )

    assert response.status_code == 400
    assert response.json == {
        "detail": "'fund_name' is a required property",
        "status": 400,
        "title": "Bad Request",
        "type": "about:blank",
    }


def test_ingest_with_r4_file_parse_auth_failure(test_client, towns_fund_round_4_file_success, test_buckets):
    """Tests that a TypeError in parse_auth() is aborted with a 400."""
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": towns_fund_round_4_file_success,
            "fund_name": "Towns Fund",
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


def test_ingest_endpoint_invalid_file_type(test_client, wrong_format_test_file, test_buckets):
    """
    Tests that, given a file of the wrong format, the endpoint returns a 400 error.
    """
    endpoint = "/ingest"
    response = test_client.post(
        endpoint,
        data={
            "excel_file": wrong_format_test_file,
            "fund_name": "Towns Fund",
            "reporting_round": 3,
        },
    )

    assert response.status_code == 400
    assert response.json == {
        "detail": "Invalid file type",
        "status": 400,
        "title": "Bad Request",
        "type": "about:blank",
    }


@pytest.mark.parametrize(
    "raised_exception",
    (
        ClientError({}, "operation_name"),
        EndpointConnectionError(endpoint_url="/"),
    ),
)
def test_ingest_endpoint_s3_upload_failure_db_rollback(
    mocker, raised_exception, test_client_rollback, towns_fund_round_4_file_success, test_buckets
) -> None:
    """
    Tests that, if a validated file fails to upload to s3 during ingest, an exception is raised and
    the database transaction will rollback and no data is committed.

    The test tries to POST a successful file to the ingest endpoint without a test bucket being created.
    This raises a ClientError and causes the session started by populate_db to rollback and no changes to be committed.

    The test compares the database before the POST (all_submissions) and after the POST (all_submissions_check) and
    asserts that these are the same, with no data having been written to the database.

    The test also asserts that the database empty. This is to safeguard against future test scope creep, and will fail
    if other tests in this module write to the database as part of the test_client fixtures. If a test writes to the
    database it should use test_client_reset instead of another test client.

    The database session started by the all_submissions query needs to be closed before the test_client_rollback POST
    to the ingest endpoint otherwise an InvalidRequestError is raised as a transaction has already begun on the session.

    """
    all_submissions = Submission.query.all()
    db.session.close()

    mocker.patch("core.aws._S3_CLIENT.upload_fileobj", side_effect=raised_exception)
    with pytest.raises((ClientError, EndpointConnectionError)):
        endpoint = "/ingest"
        test_client_rollback.post(
            endpoint,
            data={
                "excel_file": towns_fund_round_4_file_success,
                "fund_name": "Towns Fund",
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
    all_submissions_check = Submission.query.all()
    assert all_submissions == all_submissions_check == []


def test_ingest_same_programme_different_rounds(
    test_client_reset, towns_fund_round_4_file_success, towns_fund_round_3_same_programme_as_round_4_file, test_buckets
):
    """Test that ingesting the same programme in different rounds does not cause the FK relations
    of that Programme's Project's children to point to the wrong parent."""
    endpoint = "/ingest"
    test_client_reset.post(
        endpoint,
        data={
            "excel_file": towns_fund_round_3_same_programme_as_round_4_file,
            "fund_name": "Towns Fund",
            "reporting_round": 3,
            "auth": json.dumps(
                {
                    "Place Names": ["Blackfriars - Northern City Centre"],
                    "Fund Types": ["Town_Deal", "Future_High_Street_Fund"],
                }
            ),
            "do_load": True,
        },
    )

    assert len(Project.query.filter(Project.project_id == "HS-WRC-01").all()) == 1
    db.session.commit()

    test_client_reset.post(
        endpoint,
        data={
            "excel_file": towns_fund_round_4_file_success,
            "fund_name": "Towns Fund",
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

    assert len(Project.query.filter(Project.project_id == "HS-WRC-01").all()) == 2

    r3_proj_1_child = (
        ProjectProgress.query.join(Project)
        .join(ProgrammeJunction)
        .join(Submission)
        .filter(Project.project_id == "HS-WRC-01")
        .filter(Submission.reporting_round == 3)
        .first()
    )
    r4_proj_1_child = (
        ProjectProgress.query.join(Project)
        .join(ProgrammeJunction)
        .join(Submission)
        .filter(Project.project_id == "HS-WRC-01")
        .filter(Submission.reporting_round == 4)
        .first()
    )

    assert r3_proj_1_child.data_blob == {
        "adjustment_request_status": "PAR not required",
        "commentary": "asfsfsdf",
        "delivery_rag": "2",
        "delivery_status": "2. Ongoing - on track",
        "important_milestone": "sdfsdfsd",
        "risk_rag": "3",
        "spend_rag": "5",
    }
    assert r4_proj_1_child.data_blob == {
        "risk_rag": "5",
        "spend_rag": "5",
        "commentary": "Commentary on Status and RAG Ratings",
        "delivery_rag": "4",
        "delivery_stage": "Feasibility",
        "delivery_status": "3. Ongoing - delayed",
        "important_milestone": "Most Important Upcoming Comms Milestone",
        "leading_factor_of_delay": "Property Development/ Planning Permission",
        "adjustment_request_status": "PAR submitted - approved",
    }


def test_ingest_with_r3_hs_file_success_with_td_data_already_in(
    test_client_reset, towns_fund_round_3_file_success, towns_fund_td_round_3_submission_data, test_buckets
):
    """Tests that ingesting a HS file with one TD submission already in for the same round increment the submission id
    correctly."""
    endpoint = "/ingest"
    test_client_reset.post(
        endpoint,
        data={
            "excel_file": towns_fund_round_3_file_success,
            "fund_name": "Towns Fund",
            "reporting_round": 3,
            "do_load": True,
        },
    )

    assert len(Submission.query.all()) == 2
    assert Submission.query.filter(Submission.submission_id == "S-R03-2").first()
