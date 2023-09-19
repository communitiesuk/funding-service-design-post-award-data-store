import pandas as pd
import pytest

from core.const import PRE_DEFINED_FUNDING_SOURCES, StatusEnum, YesNoEnum
from core.validation.specific_validations.towns_fund_round_four import (
    TownsFundRoundFourValidationFailure,
    validate,
    validate_funding_profiles_funding_source,
    validate_locations,
    validate_programme_risks,
    validate_project_risks,
    validate_psi_funding_gap,
    validate_sign_off,
)

# flake8: noqa
from tests.validation_tests.round_four_specific_validations.mock_data import (
    invalid_review_and_sign_off_section,
    valid_review_and_sign_off_section,
)


@pytest.fixture()
def validation_functions_success_mock(mocker):
    """Mocks the validation functions to return None - which simulates successful validation."""
    functions_to_mock = [
        "core.validation.specific_validations.towns_fund_round_four.validate_project_risks",
        "core.validation.specific_validations.towns_fund_round_four.validate_programme_risks",
        "core.validation.specific_validations.towns_fund_round_four.validate_funding_profiles_funding_source",
        "core.validation.specific_validations.towns_fund_round_four.validate_sign_off",
        "core.validation.specific_validations.towns_fund_round_four.validate_psi_funding_gap",
        "core.validation.specific_validations.towns_fund_round_four.validate_locations",
    ]
    for function in functions_to_mock:
        # mock function return value
        mocker.patch(
            function,
            return_value=None,  # success
        )


def test_validate_failure(mocker, validation_functions_success_mock):
    # overwrite success mocks with failures
    mocked_failure = TownsFundRoundFourValidationFailure(tab="Test Tab", section="Test Section", message="Test Message")
    mocker.patch(
        "core.validation.specific_validations.towns_fund_round_four.validate_project_risks",
        return_value=[mocked_failure],
    )
    mocker.patch(
        "core.validation.specific_validations.towns_fund_round_four.validate_programme_risks",
        return_value=[mocked_failure],
    )

    mock_workbook = {"Sheet 1": pd.DataFrame()}
    failures = validate(mock_workbook)

    assert failures == [mocked_failure, mocked_failure]


def test_validate_success(validation_functions_success_mock):
    mock_workbook = {"Sheet 1": pd.DataFrame()}
    failures = validate(mock_workbook)
    assert failures == []


def test_validate_project_risks_returns_correct_failure():
    # project 1 completed, no risk = pass
    project_1 = {"Project ID": "TD-ABC-01"}
    project_1_progress = {"Project ID": "TD-ABC-01", "Project Delivery Status": StatusEnum.COMPLETED}

    # project 2 ongoing, risk = pass
    project_2 = {"Project ID": "TD-ABC-02"}
    project_2_progress = {"Project ID": "TD-ABC-02", "Project Delivery Status": StatusEnum.ONGOING_ON_TRACK}
    project_2_risk = {"Project ID": "TD-ABC-02"}

    # project 3 ongoing, no risk = fail
    project_3 = {"Project ID": "TD-ABC-03"}
    project_3_progress = {"Project ID": "TD-ABC-03", "Project Delivery Status": StatusEnum.ONGOING_ON_TRACK}

    # programme risk
    programme_risk = {"Project ID": pd.NA, "Programme ID": "TD-ABC"}

    project_details_df = pd.DataFrame(data=[project_1, project_2, project_3])
    project_progress_df = pd.DataFrame(data=[project_1_progress, project_2_progress, project_3_progress])
    risk_register_df = pd.DataFrame(data=[programme_risk, project_2_risk])
    workbook = {
        "Project Details": project_details_df,
        "Project Progress": project_progress_df,
        "RiskRegister": risk_register_df,
    }

    failures = validate_project_risks(workbook)

    assert failures == [
        TownsFundRoundFourValidationFailure(
            tab="Risk Register",
            section="Project Risks - Project 3",
            message="You have not entered any risks for this project. You must enter at least 1 risk per non-complete "
            "project",
        )
    ]


def test_validate_project_risks_returns_correct_failure_no_risks():
    # 3 ongoing projects
    project_progress_df = pd.DataFrame(
        data=[
            {"Project ID": "TD-ABC-01", "Project Delivery Status": StatusEnum.ONGOING_ON_TRACK},
            {"Project ID": "TD-ABC-02", "Project Delivery Status": StatusEnum.ONGOING_ON_TRACK},
            {"Project ID": "TD-ABC-03", "Project Delivery Status": StatusEnum.ONGOING_ON_TRACK},
        ]
    )
    # 3 projects
    project_details_df = pd.DataFrame(
        data=[{"Project ID": "TD-ABC-01"}, {"Project ID": "TD-ABC-02"}, {"Project ID": "TD-ABC-03"}]
    )
    # Risk Register contains no risks at all
    risk_register_df = pd.DataFrame(columns=["Project ID"])
    workbook = {
        "Project Details": project_details_df,
        "Project Progress": project_progress_df,
        "RiskRegister": risk_register_df,
    }

    failures = validate_project_risks(workbook)

    assert failures == [
        TownsFundRoundFourValidationFailure(
            tab="Risk Register",
            section="Project Risks - Project 1",
            message="You have not entered any risks for this project. You must enter at least 1 risk per non-complete "
            "project",
        ),
        TownsFundRoundFourValidationFailure(
            tab="Risk Register",
            section="Project Risks - Project 2",
            message="You have not entered any risks for this project. You must enter at least 1 risk per non-complete "
            "project",
        ),
        TownsFundRoundFourValidationFailure(
            tab="Risk Register",
            section="Project Risks - Project 3",
            message="You have not entered any risks for this project. You must enter at least 1 risk per non-complete "
            "project",
        ),
    ]


def test_validate_project_risks_returns_no_failure():
    project_details_df = pd.DataFrame(data=[{"Project ID": "TD-ABC-01"}])
    project_progress_df = pd.DataFrame(
        data=[{"Project ID": "TD-ABC-01", "Project Delivery Status": StatusEnum.ONGOING_ON_TRACK}]
    )
    risk_register_df = pd.DataFrame(data=[{"Project ID": "TD-ABC-01"}])
    workbook = {
        "Project Details": project_details_df,
        "Project Progress": project_progress_df,
        "RiskRegister": risk_register_df,
    }

    failures = validate_project_risks(workbook)

    assert failures is None


def test_validate_programme_risks_returns_correct_failure():
    # simulates risks containing 1 project risk and 0 programme risks - at least 1 programme risk is required
    risk_register_df = pd.DataFrame(data=[{"Project ID": "TD-ABC-01", "Programme ID": pd.NA}])
    workbook = {"RiskRegister": risk_register_df}

    failures = validate_programme_risks(workbook)

    assert failures == [
        TownsFundRoundFourValidationFailure(
            tab="Risk Register",
            section="Programme Risks",
            message="You have not entered enough programme level risks. "
            "You must enter at least 1 programme level risk",
        )
    ]


def test_validate_programme_risks_returns_correct_failure_no_risks():
    # Risk Register contains no risks at all
    risk_register_df = pd.DataFrame(columns=["Programme ID"])
    workbook = {"RiskRegister": risk_register_df}

    failures = validate_programme_risks(workbook)

    assert failures == [
        TownsFundRoundFourValidationFailure(
            tab="Risk Register",
            section="Programme Risks",
            message="You have not entered enough programme level risks. "
            "You must enter at least 1 programme level risk",
        )
    ]


def test_validate_programme_risks_returns_no_failure():
    # simulates risks containing 3 programme level risks
    risk_register_df = pd.DataFrame(
        data=[
            {"Project ID": pd.NA, "Programme ID": "TD-ABC"},
            {"Project ID": pd.NA, "Programme ID": "TD-ABC"},
            {"Project ID": pd.NA, "Programme ID": "TD-ABC"},
        ]
    )
    workbook = {"RiskRegister": risk_register_df}

    failures = validate_programme_risks(workbook)

    assert failures is None


def test_validate_funding_profiles_funding_source_failure():
    funding_df = pd.DataFrame(
        data=[
            # Pre-defined Funding Source
            {
                "Project ID": "TD-ABC-01",
                "Funding Source Type": "Towns Fund",
                "Funding Source Name": PRE_DEFINED_FUNDING_SOURCES[0],
            },
            # Invalid "Other Funding Source"
            {
                "Project ID": "TD-ABC-01",
                "Funding Source Type": "Invalid Funding Source Type",
                "Funding Source Name": "Some Other Funding Source",
            },
        ]
    )
    workbook = {"Funding": funding_df}

    failures = validate_funding_profiles_funding_source(workbook)

    assert failures == [
        TownsFundRoundFourValidationFailure(
            tab="Funding Profiles",
            section="Project Funding Profiles - Project 1",
            message='For column "Funding Source", you have entered "Invalid Funding Source Type" which isn\'t '
            "correct. You must select an option from the list provided",
        )
    ]


def test_validate_funding_profiles_funding_source_failure_multiple():
    funding_df = pd.DataFrame(
        data=[
            # Pre-defined Funding Source
            {
                "Project ID": "TD-ABC-01",
                "Funding Source Type": "Towns Fund",
                "Funding Source Name": PRE_DEFINED_FUNDING_SOURCES[0],
            },
            # Invalid "Other Funding Source" 1
            {
                "Project ID": "TD-ABC-03",
                "Funding Source Type": "Invalid Funding Source Type 1",
                "Funding Source Name": "Some Other Funding Source",
            },
            # Invalid "Other Funding Source" 2
            {
                "Project ID": "TD-ABC-01",
                "Funding Source Type": "Invalid Funding Source Type 2",
                "Funding Source Name": "Some Other Funding Source",
            },
        ]
    )
    workbook = {"Funding": funding_df}

    failures = validate_funding_profiles_funding_source(workbook)

    assert failures == [
        TownsFundRoundFourValidationFailure(
            tab="Funding Profiles",
            section="Project Funding Profiles - Project 3",
            message='For column "Funding Source", you have entered "Invalid Funding Source Type 1" which isn\'t '
            "correct. You must select an option from the list provided",
        ),
        TownsFundRoundFourValidationFailure(
            tab="Funding Profiles",
            section="Project Funding Profiles - Project 1",
            message='For column "Funding Source", you have entered "Invalid Funding Source Type 2" which isn\'t '
            "correct. You must select an option from the list provided",
        ),
    ]


def test_validate_funding_profiles_funding_source_success():
    funding_df = pd.DataFrame(
        data=[
            # Pre-defined Funding Source
            {
                "Project ID": "TD-ABC-01",
                "Funding Source Type": "Towns Fund",
                "Funding Source Name": PRE_DEFINED_FUNDING_SOURCES[0],
            },
            # Valid "Other Funding Source"
            {
                "Project ID": "TD-ABC-01",
                "Funding Source Type": "Local Authority",  # valid Funding Source Type
                "Funding Source Name": "Some Other Funding Source",
            },
        ]
    )
    workbook = {"Funding": funding_df}

    failures = validate_funding_profiles_funding_source(workbook)

    assert failures is None


def test_validate_sign_off_success(valid_review_and_sign_off_section):
    failures = validate_sign_off(valid_review_and_sign_off_section)

    assert failures is None


def test_validate_sign_off_failure(invalid_review_and_sign_off_section):
    failures = validate_sign_off(invalid_review_and_sign_off_section)

    assert failures == [
        TownsFundRoundFourValidationFailure(
            tab="Review & Sign-Off",
            section="Section 151 Officer / Chief Finance Officer",
            message="You must fill out the Name for this section. You "
            "need to get sign off from an S151 Officer or "
            "Chief Finance Officer",
        ),
        TownsFundRoundFourValidationFailure(
            tab="Review & Sign-Off",
            section="Town Board Chair",
            message="You must fill out the Role for this section. You need to get sign off from a programme SRO",
        ),
        TownsFundRoundFourValidationFailure(
            tab="Review & Sign-Off",
            section="Town Board Chair",
            message="You must fill out the Date for this section. You need to get sign off from a programme SRO",
        ),
    ]


def test_validate_psi_funding_gap():
    psi_df = pd.DataFrame(
        data=[
            {
                "Private Sector Funding Required": 100,
                "Private Sector Funding Secured": 0,
                "Additional Comments": pd.NA,
            },
        ]
    )
    workbook = {"Private Investments": psi_df}

    failures = validate_psi_funding_gap(workbook)

    assert failures == [
        TownsFundRoundFourValidationFailure(
            tab="PSI",
            section="Private Sector Investment",
            message=(
                'You have entered data with a greater than zero "Private Sector Investment Gap" without providing '
                "an additional comment. Use the space provided to tell us why"
            ),
        )
    ]


def test_validate_psi_funding_gap_success():
    psi_df = pd.DataFrame(
        data=[
            {
                "Private Sector Funding Required": [100, 100],
                "Private Sector Funding Secured": [0, 100],
                "Additional Comments": ["Comment", pd.NA],
            },
        ]
    )
    workbook = {"Private Investments": psi_df}

    failures = validate_psi_funding_gap(workbook)

    assert failures is None


def test_validate_locations_success():
    # validate 3 projects
    project_details_df = pd.DataFrame(
        data=[
            # Project 1: Single - valid Locations and Lat/Long data
            {
                "Single or Multiple Locations": "Multiple",
                "GIS Provided": YesNoEnum.YES,
                "Locations": "AB1 2CD",
                "Lat/Long": "Test Coords",
            },
            # Project 2: Multiple - valid Locations, Lat/Long data and GIS Provided data
            {
                "Single or Multiple Locations": "Single",
                "GIS Provided": pd.NA,
                "Locations": "AB1 2CD",
                "Lat/Long": "Test Coords",
            },
            # Project 3: Invalid Single / Multiple - invalid Locations, Lat/Long data and GIS Provided data
            # this should not produce failures because the Single / Multiple value is invalid (this is picked up during
            # schema validation)
            {"Single or Multiple Locations": "Invalid Value", "GIS Provided": pd.NA, "Locations": "", "Lat/Long": ""},
        ]
    )
    workbook = {"Project Details": project_details_df}

    failures = validate_locations(workbook)

    assert failures == []


def test_validate_locations_failure():
    # validate 3 projects
    project_details_df = pd.DataFrame(
        data=[
            # Project 1: Single - invalid Locations and Lat/Long data
            {
                "Single or Multiple Locations": "Multiple",
                "GIS Provided": pd.NA,  # empty failure"
                "Locations": pd.NA,  # empty failure
                "Lat/Long": pd.NA,  # empty failure
            },
            # Project 1: Single - invalid Locations and Lat/Long data
            {
                "Single or Multiple Locations": "Multiple",
                "GIS Provided": "Invalid enum value",  # enum failure
                "Locations": "Not empty",
                "Lat/Long": "Not empty",
            },
            # Project 2: Multiple - invalid Locations, Lat/Long data and GIS Provided data
            {
                "Single or Multiple Locations": "Single",
                "GIS Provided": pd.NA,
                "Locations": pd.NA,  # empty failure
                "Lat/Long": pd.NA,  # empty failure
            },
        ]
    )
    workbook = {"Project Details": project_details_df}

    failures = validate_locations(workbook)

    assert failures == [
        TownsFundRoundFourValidationFailure(
            tab="Project Admin",
            section="Project Details",
            message="There are blank cells in column: Single location | Project Location - Post Code (e.g. SW1P 4DF). "
            "Use the space provided to tell us the relevant information",
        ),
        TownsFundRoundFourValidationFailure(
            tab="Project Admin",
            section="Project Details",
            message="There are blank cells in column: Single location | Project Location - Lat/Long Coordinates "
            "(3.d.p e.g. 51.496, -0.129). "
            "Use the space provided to tell us the relevant information",
        ),
        TownsFundRoundFourValidationFailure(
            tab="Project Admin",
            section="Project Details",
            message="There are blank cells in column: Multiple locations | Project Locations - Post Code (e.g. "
            "SW1P 4DF). "
            "Use the space provided to tell us the relevant information",
        ),
        TownsFundRoundFourValidationFailure(
            tab="Project Admin",
            section="Project Details",
            message="There are blank cells in column: Multiple locations | Project Locations - Lat/Long Coordinates "
            "(3.d.p e.g. 51.496, -0.129). "
            "Use the space provided to tell us the relevant information",
        ),
        TownsFundRoundFourValidationFailure(
            tab="Project Admin",
            section="Project Details",
            message="There are blank cells in column: Multiple locations | Are you providing a GIS map (see guidance) "
            "with your return?. "
            "Use the space provided to tell us the relevant information",
        ),
        TownsFundRoundFourValidationFailure(
            tab="Project Admin",
            section="Project Details",
            message='For column "Multiple locations | Are you providing a GIS map (see guidance) with your '
            'return?", you have entered "Invalid enum value" which isn\'t correct. '
            "You must select an option from the list provided",
        ),
    ]
