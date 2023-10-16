import pandas as pd
import pytest

from core.const import PRE_DEFINED_FUNDING_SOURCES, StatusEnum, YesNoEnum
from core.validation.specific_validations.towns_fund_round_four import (
    TownsFundRoundFourValidationFailure,
    validate,
    validate_funding_profiles_funding_source,
    validate_funding_spent,
    validate_leading_factor_of_delay,
    validate_locations,
    validate_programme_risks,
    validate_project_risks,
    validate_psi_funding_gap,
)


@pytest.fixture()
def validation_functions_success_mock(mocker):
    """Mocks the validation functions to return None - which simulates successful validation."""
    functions_to_mock = [
        "core.validation.specific_validations.towns_fund_round_four.validate_project_risks",
        "core.validation.specific_validations.towns_fund_round_four.validate_programme_risks",
        "core.validation.specific_validations.towns_fund_round_four.validate_funding_profiles_funding_source",
        "core.validation.specific_validations.towns_fund_round_four.validate_psi_funding_gap",
        "core.validation.specific_validations.towns_fund_round_four.validate_locations",
        "core.validation.specific_validations.towns_fund_round_four.validate_leading_factor_of_delay",
        "core.validation.specific_validations.towns_fund_round_four.validate_funding_spent",
    ]
    for function in functions_to_mock:
        # mock function return value
        mocker.patch(
            function,
            return_value=None,  # success
        )


def test_validate_failure(mocker, validation_functions_success_mock):
    # overwrite success mocks with failures
    mocked_failure = TownsFundRoundFourValidationFailure(
        sheet="Test sheet", section="Test Section", column="Test column", message="Test Message", row_indexes=1
    )
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
            sheet="RiskRegister",
            section="Project Risks - Project 3",
            column="RiskName",
            message="You have not entered any risks for this project. You must enter at least 1 risk per non-complete "
            "project",
            row_indexes=[37],
        )
    ]


def test_validate_project_risks_returns_correct_failure_no_risks():
    # 3 ongoing projects
    project_progress_df = pd.DataFrame(
        data=[
            {"Project ID": "TD-ABC-01", "Project Delivery Status": StatusEnum.ONGOING_ON_TRACK},
            {"Project ID": "TD-ABC-03", "Project Delivery Status": StatusEnum.ONGOING_ON_TRACK},
            {"Project ID": "TD-ABC-04", "Project Delivery Status": StatusEnum.ONGOING_ON_TRACK},
        ]
    )
    # 3 projects
    project_details_df = pd.DataFrame(
        data=[{"Project ID": "TD-ABC-01"}, {"Project ID": "TD-ABC-03"}, {"Project ID": "TD-ABC-04"}]
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
            sheet="RiskRegister",
            section="Project Risks - Project 1",
            column="RiskName",
            message="You have not entered any risks for this project. You must enter at least 1 risk per non-complete "
            "project",
            row_indexes=[21],
        ),
        TownsFundRoundFourValidationFailure(
            sheet="RiskRegister",
            section="Project Risks - Project 3",
            column="RiskName",
            message="You have not entered any risks for this project. You must enter at least 1 risk per non-complete "
            "project",
            row_indexes=[37],
        ),
        TownsFundRoundFourValidationFailure(
            sheet="RiskRegister",
            section="Project Risks - Project 4",
            column="RiskName",
            message="You have not entered any risks for this project. You must enter at least 1 risk per non-complete "
            "project",
            row_indexes=[46],
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
            sheet="RiskRegister",
            section="Programme Risks",
            column="RiskName",
            message="You have not entered enough programme level risks. "
            "You must enter at least 1 programme level risk",
            row_indexes=[10],
        )
    ]


def test_validate_programme_risks_returns_correct_failure_no_risks():
    # Risk Register contains no risks at all
    risk_register_df = pd.DataFrame(columns=["Programme ID"])
    workbook = {"RiskRegister": risk_register_df}

    failures = validate_programme_risks(workbook)

    assert failures == [
        TownsFundRoundFourValidationFailure(
            sheet="RiskRegister",
            section="Programme Risks",
            column="RiskName",
            message="You have not entered enough programme level risks. "
            "You must enter at least 1 programme level risk",
            row_indexes=[10],
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
        index=[5, 6],
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
        ],
    )
    workbook = {"Funding": funding_df}

    failures = validate_funding_profiles_funding_source(workbook)

    assert failures == [
        TownsFundRoundFourValidationFailure(
            sheet="Funding",
            section="Project Funding Profiles - Project 1",
            column="Funding Source Type",
            message='For column "Funding Source", you have entered "Invalid Funding Source Type" which isn\'t '
            "correct. You must select an option from the list provided",
            row_indexes=[6],
        )
    ]


def test_validate_funding_profiles_funding_source_failure_multiple():
    funding_df = pd.DataFrame(
        index=[3, 5, 7],
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
        ],
    )
    workbook = {"Funding": funding_df}

    failures = validate_funding_profiles_funding_source(workbook)

    assert failures == [
        TownsFundRoundFourValidationFailure(
            sheet="Funding",
            section="Project Funding Profiles - Project 3",
            column="Funding Source Type",
            message='For column "Funding Source", you have entered "Invalid Funding Source Type 1" which isn\'t '
            "correct. You must select an option from the list provided",
            row_indexes=[5],
        ),
        TownsFundRoundFourValidationFailure(
            sheet="Funding",
            section="Project Funding Profiles - Project 1",
            column="Funding Source Type",
            message='For column "Funding Source", you have entered "Invalid Funding Source Type 2" which isn\'t '
            "correct. You must select an option from the list provided",
            row_indexes=[7],
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


def test_validate_psi_funding_gap():
    psi_df = pd.DataFrame(
        index=[10],
        data=[
            {
                "Private Sector Funding Required": 100,
                "Private Sector Funding Secured": 0,
                "Additional Comments": pd.NA,
            },
        ],
    )
    workbook = {"Private Investments": psi_df}

    failures = validate_psi_funding_gap(workbook)

    assert failures == [
        TownsFundRoundFourValidationFailure(
            sheet="Private Investments",
            section="Private Sector Investment",
            column="Additional Comments",
            message=(
                'You have entered data with a greater than zero "Private Sector Investment Gap" without providing '
                "an additional comment. Use the space provided to tell us why"
            ),
            row_indexes=[10],
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
        index=[1, 2, 3, 4],
        data=[
            # Project 1: Multiple - invalid Locations and Lat/Long data
            {
                "Single or Multiple Locations": "Multiple",
                "GIS Provided": pd.NA,  # empty failure"
                "Locations": pd.NA,  # empty failure
                "Lat/Long": pd.NA,  # empty failure
            },
            # Project 1: Multiple - invalid Locations and Lat/Long data
            {
                "Single or Multiple Locations": "Multiple",
                "GIS Provided": pd.NA,  # empty failure"
                "Locations": pd.NA,  # empty failure
                "Lat/Long": pd.NA,  # empty failure
            },
            # Project 2: Single - invalid Locations, Lat/Long data and GIS Provided data
            {
                "Single or Multiple Locations": "Single",
                "GIS Provided": pd.NA,
                "Locations": pd.NA,  # empty failure
                "Lat/Long": pd.NA,  # empty failure
            },
            # Project 3: Single - invalid Locations, GIS Provided data
            {
                "Single or Multiple Locations": "Multiple",
                "GIS Provided": "Invalid enum value",  # enum failure
                "Locations": "Not empty",
                "Lat/Long": "Not empty",
            },
        ],
    )
    workbook = {"Project Details": project_details_df}

    failures = validate_locations(workbook)

    assert failures == [
        TownsFundRoundFourValidationFailure(
            sheet="Project Details",
            section="Project Details",
            column="Locations",
            message="There are blank cells in column: Single location | Project Location - Post Code (e.g. SW1P 4DF). "
            "Use the space provided to tell us the relevant information",
            row_indexes=[3],
        ),
        TownsFundRoundFourValidationFailure(
            sheet="Project Details",
            section="Project Details",
            column="Lat/Long",
            message="There are blank cells in column: Single location | Project Location - Lat/Long Coordinates "
            "(3.d.p e.g. 51.496, -0.129). "
            "Use the space provided to tell us the relevant information",
            row_indexes=[3],
        ),
        TownsFundRoundFourValidationFailure(
            sheet="Project Details",
            section="Project Details",
            column="Locations",
            message="There are blank cells in column: Multiple locations | Project Locations - Post Code (e.g. "
            "SW1P 4DF). "
            "Use the space provided to tell us the relevant information",
            row_indexes=[1, 2],
        ),
        TownsFundRoundFourValidationFailure(
            sheet="Project Details",
            section="Project Details",
            column="Lat/Long",
            message="There are blank cells in column: Multiple locations | Project Locations - Lat/Long Coordinates "
            "(3.d.p e.g. 51.496, -0.129). "
            "Use the space provided to tell us the relevant information",
            row_indexes=[1, 2],
        ),
        TownsFundRoundFourValidationFailure(
            sheet="Project Details",
            section="Project Details",
            column="GIS Provided",
            message="There are blank cells in column: Multiple locations | Are you providing a GIS map (see guidance) "
            "with your return?. "
            "Use the space provided to tell us the relevant information",
            row_indexes=[1, 2],
        ),
        TownsFundRoundFourValidationFailure(
            sheet="Project Details",
            section="Project Details",
            column="GIS Provided",
            message='For column "Multiple locations | Are you providing a GIS map (see guidance) with your '
            'return?", you have entered "Invalid enum value" which isn\'t correct. '
            "You must select an option from the list provided",
            row_indexes=[4],
        ),
    ]


def test_validate_leading_factor_of_delay_success():
    project_details_df = pd.DataFrame(
        data=[
            # Project 1: "Delayed" with delay value
            {
                "Project Delivery Status": StatusEnum.ONGOING_DELAYED,
                "Leading Factor of Delay": "some delay",
            },
            # Project 2: "Not started" with delay value
            {
                "Project Delivery Status": StatusEnum.NOT_YET_STARTED,
                "Leading Factor of Delay": "some delay",
            },
            # Project 3: "Completed" with no delay value
            {
                "Project Delivery Status": StatusEnum.COMPLETED,
                "Leading Factor of Delay": "",  # no delay
            },
        ]
    )
    workbook = {"Project Progress": project_details_df}

    failures = validate_leading_factor_of_delay(workbook)

    assert failures is None


def test_validate_leading_factor_of_delay_delayed_failure():
    project_details_df = pd.DataFrame(
        data=[
            # Project 1: "Delayed" with no delay value
            {
                "Project Delivery Status": StatusEnum.ONGOING_DELAYED,
                "Leading Factor of Delay": "",
            },
            # Project 2: "Completed" with no delay value
            {
                "Project Delivery Status": StatusEnum.COMPLETED,
                "Leading Factor of Delay": "",  # no delay
            },
        ]
    )
    workbook = {"Project Progress": project_details_df}

    failures = validate_leading_factor_of_delay(workbook)

    assert failures == [
        TownsFundRoundFourValidationFailure(
            sheet="Programme Progress",
            section="Projects Progress Summary",
            column="Leading Factor of Delay",
            message='Projects with Project Delivery Status as "1. Not yet started" or "3. Ongoing - delayed" must not '
            "contain blank cells for the column: Leading Factor of Delay. Use the space provided to tell us the"
            " relevant information",
            row_indexes=[0],
        )
    ]


def test_validate_leading_factor_of_delay_not_yet_started_failure():
    project_details_df = pd.DataFrame(
        data=[
            # Project 1: "Not yet started" with no delay value
            {
                "Project Delivery Status": StatusEnum.NOT_YET_STARTED,
                "Leading Factor of Delay": "< Select >",
            },
            # Project 2: "Completed" with no delay value
            {
                "Project Delivery Status": StatusEnum.COMPLETED,
                "Leading Factor of Delay": "",  # no delay
            },
        ]
    )
    workbook = {"Project Progress": project_details_df}

    failures = validate_leading_factor_of_delay(workbook)

    assert failures == [
        TownsFundRoundFourValidationFailure(
            sheet="Programme Progress",
            section="Projects Progress Summary",
            column="Leading Factor of Delay",
            message='Projects with Project Delivery Status as "1. Not yet started" or "3. Ongoing - delayed" must not '
            "contain blank cells for the column: Leading Factor of Delay. Use the space provided to tell us the"
            " relevant information",
            row_indexes=[0],
        )
    ]


@pytest.fixture
def allocated_funding():
    allocated_funding = pd.DataFrame(
        {"Index Code": ["TD-FAK-01", "TD-FAK-02", "TD-FAK-03", "HS-FAK"], "Grant Awarded": [123, 123, 123, 123]}
    ).set_index("Index Code")["Grant Awarded"]
    return allocated_funding


def test_validate_funding_spent(mocker, allocated_funding):
    mocker.patch(
        "core.validation.specific_validations.towns_fund_round_four.get_allocated_funding",
        return_value=allocated_funding,
    )

    funding_df = pd.DataFrame(
        data=[
            # Project 1 over spent will trigger validation
            {
                "Project ID": "TD-FAK-01",
                "Funding Source Type": "Towns Fund",
                "Funding Source Name": "funding",
                "Spend for Reporting Period": 124,
            },
            # Project 2 over spent but contractually committed, won't trigger validation
            {
                "Project ID": "TD-FAK-02",
                "Funding Source Type": "Towns Fund",
                "Funding Source Name": "funding that is contractually committed",
                "Spend for Reporting Period": 124,
            },
            # Project 3 only towns fund funding, will trigger validation
            {
                "Project ID": "TD-FAK-03",
                "Funding Source Type": "Towns Fund",
                "Funding Source Name": "example funding",
                "Spend for Reporting Period": 124,
            },
            {
                "Project ID": "TD-FAK-03",
                "Funding Source Type": "Other funding source",
                "Funding Source Name": "example funding",
                "Spend for Reporting Period": 124,
            },
        ]
    )

    workbook = {
        "Programme_Ref": pd.DataFrame([{"Programme ID": "TD-FAK", "FundType_ID": "TD"}]),
        "Project Details": pd.DataFrame(
            [{"Project ID": "TD-FAK-01"}, {"Project ID": "TD-FAK-02"}, {"Project ID": "TD-FAK-03"}]
        ),
        "Funding": funding_df,
    }

    failures = validate_funding_spent(workbook)

    assert failures == [
        TownsFundRoundFourValidationFailure(
            sheet="Funding",
            section="Project Funding Profiles - Project 1",
            column="Grand Total",
            message=(
                "The total spend for this project is higher than amount allocated for the project. Please"
                " check the total spend and resubmit your spreadsheet. You spent 124 but were only allocated 123"
            ),
            row_indexes=[43],
        ),
        TownsFundRoundFourValidationFailure(
            sheet="Funding",
            section="Project Funding Profiles - Project 3",
            column="Grand Total",
            message=(
                "The total spend for this project is higher than amount allocated for the project. Please"
                " check the total spend and resubmit your spreadsheet. You spent 124 but were only allocated 123"
            ),
            row_indexes=[99],
        ),
    ]


def test_validate_funding_spent_FHSF(mocker, allocated_funding):
    mocker.patch(
        "core.validation.specific_validations.towns_fund_round_four.get_allocated_funding",
        return_value=allocated_funding,
    )

    funding_df = pd.DataFrame(
        data=[
            # Overspent at the programme level sum of all three project spend
            # Project 1
            {
                "Project ID": "HS-FAK-01",
                "Funding Source Type": "Towns Fund",
                "Funding Source Name": "funding",
                "Spend for Reporting Period": 100,
            },
            # Project 2
            {
                "Project ID": "HS-FAK-02",
                "Funding Source Type": "Towns Fund",
                "Funding Source Name": "funding",
                "Spend for Reporting Period": 100,
            },
            # Project 3
            {
                "Project ID": "HS-FAK-03",
                "Funding Source Type": "Towns Fund",
                "Funding Source Name": "funding",
                "Spend for Reporting Period": 100,
            },
        ]
    )

    workbook = {
        "Programme_Ref": pd.DataFrame([{"Programme ID": "HS-FAK", "FundType_ID": "HS"}]),
        "Project Details": pd.DataFrame(
            [{"Project ID": "HS-FAK-01"}, {"Project ID": "HS-FAK-02"}, {"Project ID": "HS-FAK-03"}]
        ),
        "Funding": funding_df,
    }

    failures = validate_funding_spent(workbook)

    assert failures == [
        TownsFundRoundFourValidationFailure(
            sheet="Funding",
            section="Project Funding Profiles",
            column="Grand Total",
            message=(
                "The total spend for this programme is higher than amount allocated for the programme. Please"
                " check the total spend and resubmit your spreadsheet. You spent 300 but were only allocated 123"
            ),
            row_indexes=[43, 71, 99],
        )
    ]
