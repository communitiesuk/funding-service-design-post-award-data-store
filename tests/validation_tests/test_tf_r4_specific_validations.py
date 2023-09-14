import pandas as pd
import pytest

from core.const import PRE_DEFINED_FUNDING_SOURCES
from core.validation.specific_validations.towns_fund_round_four import (
    TownsFundRoundFourValidationFailure,
    validate,
    validate_funding_profiles_funding_source,
    validate_programme_risks,
    validate_project_admin_gis_provided,
    validate_project_risks,
)


@pytest.fixture()
def validation_functions_success_mock(mocker):
    """Mocks the validation functions to return None - which simulates successful validation."""
    functions_to_mock = [
        "core.validation.specific_validations.towns_fund_round_four.validate_project_risks",
        "core.validation.specific_validations.towns_fund_round_four.validate_programme_risks",
        "core.validation.specific_validations.towns_fund_round_four.validate_project_admin_gis_provided",
        "core.validation.specific_validations.towns_fund_round_four.validate_funding_profiles_funding_source",
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
    project_details_df = pd.DataFrame(data=[{"Project ID": "TD-ABC-01"}, {"Project ID": "TD-ABC-02"}])
    # Risk Register is missing a risk for Project 2
    # {"Project ID": pd.NA} simulates a programme level risk
    risk_register_df = pd.DataFrame(data=[{"Project ID": pd.NA}, {"Project ID": "TD-ABC-01"}])
    workbook = {"Project Details": project_details_df, "RiskRegister": risk_register_df}

    failures = validate_project_risks(workbook)

    assert failures == [
        TownsFundRoundFourValidationFailure(
            tab="Risk Register",
            section="Project Risks - Project 2",
            message="You have not entered any risks for this project. You must enter at least 1 risk per project",
        )
    ]


def test_validate_project_risks_returns_correct_failure_no_risks():
    project_details_df = pd.DataFrame(
        data=[{"Project ID": "TD-ABC-01"}, {"Project ID": "TD-ABC-02"}, {"Project ID": "TD-ABC-03"}]
    )
    # Risk Register contains no risks at all
    risk_register_df = pd.DataFrame(columns=["Project ID"])
    workbook = {"Project Details": project_details_df, "RiskRegister": risk_register_df}

    failures = validate_project_risks(workbook)

    assert failures == [
        TownsFundRoundFourValidationFailure(
            tab="Risk Register",
            section="Project Risks - Project 1",
            message="You have not entered any risks for this project. You must enter at least 1 risk per project",
        ),
        TownsFundRoundFourValidationFailure(
            tab="Risk Register",
            section="Project Risks - Project 2",
            message="You have not entered any risks for this project. You must enter at least 1 risk per project",
        ),
        TownsFundRoundFourValidationFailure(
            tab="Risk Register",
            section="Project Risks - Project 3",
            message="You have not entered any risks for this project. You must enter at least 1 risk per project",
        ),
    ]


def test_validate_project_risks_returns_no_failure():
    project_details_df = pd.DataFrame(data=[{"Project ID": "TD-ABC-01"}])
    risk_register_df = pd.DataFrame(data=[{"Project ID": "TD-ABC-01"}])
    workbook = {"Project Details": project_details_df, "RiskRegister": risk_register_df}

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
            "You must enter at least 1 programme level risks",
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
            "You must enter at least 1 programme level risks",
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


def test_validate_project_admin_gis_provided_returns_correct_failure():
    # contains two projects, one with multiple location and no GIS data (causing a failure), the other is single with
    # no GIS data
    project_details_df = pd.DataFrame(
        data=[
            {"Single or Multiple Locations": "Multiple", "GIS Provided": pd.NA},
            {"Single or Multiple Locations": "Single", "GIS Provided": pd.NA},
        ]
    )
    workbook = {"Project Details": project_details_df}

    failures = validate_project_admin_gis_provided(workbook)

    assert failures == [
        TownsFundRoundFourValidationFailure(
            tab="Project Admin",
            section="Project Details",
            message='There are blank cells in column: "Are you providing a GIS map (see guidance) with your '
            'return?". Use the space provided to tell us the relevant information',
        )
    ]


def test_validate_project_admin_gis_provided_returns_no_failure():
    # contains two projects, one with multiple location and GIS data, the other is single with
    # no GIS data
    project_details_df = pd.DataFrame(
        data=[
            {"Single or Multiple Locations": "Multiple", "GIS Provided": "Yes"},
            {"Single or Multiple Locations": "Single", "GIS Provided": pd.NA},
        ]
    )
    workbook = {"Project Details": project_details_df}

    failures = validate_project_admin_gis_provided(workbook)

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
