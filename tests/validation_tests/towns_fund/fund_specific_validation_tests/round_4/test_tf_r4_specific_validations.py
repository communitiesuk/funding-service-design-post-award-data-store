import pandas as pd
import pytest

from core.const import StatusEnum, YesNoEnum
from core.messaging.tf_messaging import TFMessages as msgs
from core.validation.towns_fund.fund_specific_validation.round_4.validate import (
    PRE_DEFINED_FUNDING_SOURCES,
    GenericFailure,
    validate,
    validate_funding_profiles_at_least_one_other_funding_source_fhsf,
    validate_funding_profiles_funding_secured_not_null,
    validate_funding_profiles_funding_source_enum,
    validate_funding_questions,
    validate_funding_spent,
    validate_locations,
    validate_postcodes,
    validate_programme_risks,
    validate_project_progress,
    validate_project_risks,
    validate_psi_funding_gap,
    validate_psi_funding_not_negative,
    validate_sign_off,
)


@pytest.fixture()
def validation_functions_success_mock(mocker):
    """Mocks the validation functions to return None - which simulates successful validation."""
    mocker.patch(
        "core.validation.towns_fund.fund_specific_validation.round_4.validate.validate_sign_off",
        return_value=[],
    )
    functions_to_mock = [
        "core.validation.towns_fund.fund_specific_validation.round_4.validate.validate_project_risks",
        "core.validation.towns_fund.fund_specific_validation.round_4.validate.validate_programme_risks",
        "core.validation.towns_fund.fund_specific_validation.round_4.validate"
        ".validate_funding_profiles_funding_source_enum",
        "core.validation.towns_fund.fund_specific_validation.round_4.validate"
        ".validate_funding_profiles_at_least_one_other_funding_source_fhsf",
        "core.validation.towns_fund.fund_specific_validation.round_4.validate.validate_psi_funding_gap",
        "core.validation.towns_fund.fund_specific_validation.round_4.validate.validate_locations",
        "core.validation.towns_fund.fund_specific_validation.round_4.validate.validate_funding_spent",
        "core.validation.towns_fund.fund_specific_validation.round_4"
        ".validate.validate_funding_profiles_funding_secured_not_null",
        "core.validation.towns_fund.fund_specific_validation.round_4.validate.validate_postcodes",
        "core.validation.towns_fund.fund_specific_validation.round_4.validate.validate_psi_funding_not_negative",
        "core.validation.towns_fund.fund_specific_validation.round_4.validate.validate_funding_questions",
        "core.validation.towns_fund.fund_specific_validation.round_4.validate.validate_project_progress",
    ]
    for function in functions_to_mock:
        # mock function return value
        mocker.patch(
            function,
            return_value=None,  # success
        )


def test_validate_failure(mocker, validation_functions_success_mock):
    # overwrite success mocks with failures
    mocked_failure = GenericFailure(
        table="Test sheet", section="Test Section", column="Test column", message="Test Message", row_index=1
    )
    mocker.patch(
        "core.validation.towns_fund.fund_specific_validation.round_4.validate.validate_project_risks",
        return_value=[mocked_failure],
    )
    mocker.patch(
        "core.validation.towns_fund.fund_specific_validation.round_4.validate.validate_programme_risks",
        return_value=[mocked_failure],
    )
    mocker.patch(
        "core.validation.towns_fund.fund_specific_validation.round_4.validate.validate_sign_off",
        return_value=[],
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
        GenericFailure(
            table="RiskRegister",
            section="Project Risks - Project 3",
            column="RiskName",
            message=msgs.PROJECT_RISKS,
            row_index=37,
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
        GenericFailure(
            table="RiskRegister",
            section="Project Risks - Project 1",
            column="RiskName",
            message=msgs.PROJECT_RISKS,
            row_index=21,
        ),
        GenericFailure(
            table="RiskRegister",
            section="Project Risks - Project 2",
            column="RiskName",
            message=msgs.PROJECT_RISKS,
            row_index=29,
        ),
        GenericFailure(
            table="RiskRegister",
            section="Project Risks - Project 3",
            column="RiskName",
            message=msgs.PROJECT_RISKS,
            row_index=37,
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
        GenericFailure(
            table="RiskRegister",
            section="Programme Risks",
            column="RiskName",
            message=msgs.PROGRAMME_RISKS,
            row_index=10,
        )
    ]


def test_validate_programme_risks_returns_correct_failure_no_risks():
    # Risk Register contains no risks at all
    risk_register_df = pd.DataFrame(columns=["Programme ID"])
    workbook = {"RiskRegister": risk_register_df}

    failures = validate_programme_risks(workbook)

    assert failures == [
        GenericFailure(
            table="RiskRegister",
            section="Programme Risks",
            column="RiskName",
            message=msgs.PROGRAMME_RISKS,
            row_index=10,
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
        index=[48, 49],
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

    failures = validate_funding_profiles_funding_source_enum(workbook)

    assert failures == [
        GenericFailure(
            table="Funding",
            section="Project Funding Profiles - Project 1",
            column="Funding Source Type",
            message=msgs.DROPDOWN,
            row_index=49,
        )
    ]


def test_validate_funding_profiles_funding_source_failure_multiple():
    funding_df = pd.DataFrame(
        index=[48, 48, 106],  # includes duplicate indexes
        data=[
            # Pre-defined Funding Source
            {
                "Project ID": "TD-ABC-01",
                "Funding Source Type": "Invalid Funding Source Type 1",
                "Funding Source Name": "Some Other Funding Source",
            },
            # Invalid "Other Funding Source" 1
            {
                "Project ID": "TD-ABC-01",
                "Funding Source Type": "Invalid Funding Source Type 1",
                "Funding Source Name": "Some Other Funding Source",
            },
            # Invalid "Other Funding Source" 2
            {
                "Project ID": "TD-ABC-03",
                "Funding Source Type": "Invalid Funding Source Type 2",
                "Funding Source Name": "Some Other Funding Source",
            },
        ],
    )
    workbook = {"Funding": funding_df}

    failures = validate_funding_profiles_funding_source_enum(workbook)

    assert failures == [
        GenericFailure(
            table="Funding",
            section="Project Funding Profiles - Project 1",
            column="Funding Source Type",
            message=msgs.DROPDOWN,
            row_index=48,
        ),
        GenericFailure(
            table="Funding",
            section="Project Funding Profiles - Project 3",
            column="Funding Source Type",
            message=msgs.DROPDOWN,
            row_index=106,
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

    failures = validate_funding_profiles_funding_source_enum(workbook)

    assert failures is None


def test_validate_funding_profiles_at_least_one_other_funding_source_fhsf_success_non_fhsf():
    programme_ref_df = pd.DataFrame(data=[{"FundType_ID": "TD"}])
    workbook = {"Programme_Ref": programme_ref_df}

    failures = validate_funding_profiles_at_least_one_other_funding_source_fhsf(workbook)

    assert failures is None


def test_validate_funding_profiles_at_least_one_other_funding_source_fhsf_success():
    programme_ref_df = pd.DataFrame(data=[{"FundType_ID": "HS"}])
    funding_df = pd.DataFrame(
        data=[
            # Pre-defined Funding Source
            {
                "Funding Source Name": PRE_DEFINED_FUNDING_SOURCES[0],
            },
            # "Other Funding Source"
            {
                "Funding Source Name": "Some Other Funding Source",
            },
        ]
    )

    workbook = {"Programme_Ref": programme_ref_df, "Funding": funding_df}

    failures = validate_funding_profiles_at_least_one_other_funding_source_fhsf(workbook)

    assert failures is None


def test_validate_funding_profiles_at_least_one_other_funding_source_fhsf_failure():
    programme_ref_df = pd.DataFrame(data=[{"FundType_ID": "HS"}])
    funding_df = pd.DataFrame(
        data=[
            # Pre-defined Funding Source
            {
                "Funding Source Name": PRE_DEFINED_FUNDING_SOURCES[0],
            },
        ]
    )

    workbook = {"Programme_Ref": programme_ref_df, "Funding": funding_df}

    failures = validate_funding_profiles_at_least_one_other_funding_source_fhsf(workbook)

    assert failures == [
        GenericFailure(
            table="Funding",
            section="Project Funding Profiles",
            column="Funding Source Type",
            message=msgs.MISSING_OTHER_FUNDING_SOURCES,
            row_index=None,
        )
    ]


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
        GenericFailure(
            table="Private Investments",
            section="Private Sector Investment",
            column="Additional Comments",
            message=msgs.BLANK_PSI,
            row_index=10,
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
                "Lat/Long": pd.NA,  # no failure
            },
            # Project 1: Multiple - invalid Locations and Lat/Long data
            {
                "Single or Multiple Locations": "Multiple",
                "GIS Provided": pd.NA,  # empty failure"
                "Locations": pd.NA,  # empty failure
                "Lat/Long": pd.NA,  # no failure
            },
            # Project 2: Single - invalid Locations, Lat/Long data and GIS Provided data
            {
                "Single or Multiple Locations": "Single",
                "GIS Provided": pd.NA,
                "Locations": pd.NA,  # empty failure
                "Lat/Long": pd.NA,  # no failure
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
        GenericFailure(
            table="Project Details",
            section="Project Details",
            column="Locations",
            message=msgs.BLANK,
            row_index=3,
        ),
        GenericFailure(
            table="Project Details",
            section="Project Details",
            column="Locations",
            message=msgs.BLANK,
            row_index=1,
        ),
        GenericFailure(
            table="Project Details",
            section="Project Details",
            column="Locations",
            message=msgs.BLANK,
            row_index=2,
        ),
        GenericFailure(
            table="Project Details",
            section="Project Details",
            column="GIS Provided",
            message=msgs.BLANK,
            row_index=1,
        ),
        GenericFailure(
            table="Project Details",
            section="Project Details",
            column="GIS Provided",
            message=msgs.BLANK,
            row_index=2,
        ),
        GenericFailure(
            table="Project Details",
            section="Project Details",
            column="GIS Provided",
            message=msgs.DROPDOWN,
            row_index=4,
        ),
    ]


@pytest.fixture
def allocated_funding():
    allocated_funding = pd.DataFrame(
        {
            "Index Code": ["TD-FAK-01", "TD-FAK-02", "TD-FAK-03", "HS-FAK"],
            "RDEL": [123, 123, 123, 0],
            "CDEL": [123, 123, 123, 0],
            "Total": [246, 246, 246, 123],
        }
    ).set_index("Index Code")
    return allocated_funding


def test_validate_funding_spent(mocker, allocated_funding):
    mocker.patch(
        "core.validation.towns_fund.fund_specific_validation.round_4.validate.FUNDING_ALLOCATION",
        allocated_funding,
    )

    funding_df = pd.DataFrame(
        data=[
            # Project 1 over spent will trigger validation CDEL and RDEL
            {
                "Project ID": "TD-FAK-01",
                "Funding Source Type": "Towns Fund",
                "Funding Source Name": "funding CDEL",
                "Spend for Reporting Period": 124,
            },
            {
                "Project ID": "TD-FAK-01",
                "Funding Source Type": "Towns Fund",
                "Funding Source Name": "funding RDEL",
                "Spend for Reporting Period": 124,
            },
            # Project 3 only towns fund funding, will trigger validation
            {
                "Project ID": "TD-FAK-03",
                "Funding Source Type": "Towns Fund",
                "Funding Source Name": "example funding RDEL",
                "Spend for Reporting Period": 124,
            },
            {
                "Project ID": "TD-FAK-03",
                "Funding Source Type": "Other funding source",
                "Funding Source Name": "example funding CDEL",
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
        GenericFailure(
            table="Funding",
            section="Project Funding Profiles - Project 1",
            column="Grand Total",
            message=msgs.OVERSPEND.format(expense_type="CDEL"),
            row_index=41,
        ),
        GenericFailure(
            table="Funding",
            section="Project Funding Profiles - Project 1",
            column="Grand Total",
            message=msgs.OVERSPEND.format(expense_type="RDEL"),
            row_index=44,
        ),
        GenericFailure(
            table="Funding",
            section="Project Funding Profiles - Project 3",
            column="Grand Total",
            message=msgs.OVERSPEND.format(expense_type="RDEL"),
            row_index=100,
        ),
    ]


def test_validate_funding_spent_floating_point_precision(mocker, allocated_funding):
    mocker.patch(
        "core.validation.towns_fund.fund_specific_validation.round_4.validate.FUNDING_ALLOCATION",
        allocated_funding,
    )

    funding_df = pd.DataFrame(
        data=[
            # Should not trigger failure for overspending due to floating points being rounded to 2dp
            {
                "Project ID": "TD-FAK-01",
                "Funding Source Type": "Towns Fund",
                "Funding Source Name": "funding CDEL",
                "Spend for Reporting Period": 123.0000000001,
            },
        ]
    )

    workbook = {
        "Programme_Ref": pd.DataFrame([{"Programme ID": "TD-FAK", "FundType_ID": "TD"}]),
        "Project Details": pd.DataFrame([{"Project ID": "TD-FAK-01"}]),
        "Funding": funding_df,
    }

    failures = validate_funding_spent(workbook)

    assert not failures


def test_validate_funding_spent_FHSF(mocker, allocated_funding):
    mocker.patch(
        "core.validation.towns_fund.fund_specific_validation.round_4.validate.FUNDING_ALLOCATION",
        allocated_funding,
    )

    funding_df = pd.DataFrame(
        data=[
            # Overspent at the programme level sum of all three project spend
            # Project 1
            {
                "Project ID": "HS-FAK-01",
                "Funding Source Type": "Towns Fund",
                "Funding Source Name": "funding CDEL",
                "Spend for Reporting Period": 100,
            },
            # Project 2
            {
                "Project ID": "HS-FAK-02",
                "Funding Source Type": "Towns Fund",
                "Funding Source Name": "funding RDEL",
                "Spend for Reporting Period": 100,
            },
            # Project 3
            {
                "Project ID": "HS-FAK-03",
                "Funding Source Type": "Towns Fund",
                "Funding Source Name": "funding CDEL",
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
        GenericFailure(
            table="Funding",
            section="Project Funding Profiles",
            column="Grand Total",
            message=msgs.OVERSPEND_PROGRAMME,
            row_index=45,
        ),
        GenericFailure(
            table="Funding",
            section="Project Funding Profiles",
            column="Grand Total",
            message=msgs.OVERSPEND_PROGRAMME,
            row_index=73,
        ),
        GenericFailure(
            table="Funding",
            section="Project Funding Profiles",
            column="Grand Total",
            message=msgs.OVERSPEND_PROGRAMME,
            row_index=101,
        ),
    ]


def test_validate_funding_spent_no_errors(mocker, allocated_funding):
    mocker.patch(
        "core.validation.towns_fund.fund_specific_validation.round_4.validate.FUNDING_ALLOCATION",
        allocated_funding,
    )
    funding_df = pd.DataFrame(
        data=[
            # Under spent or exactly as allocated, won't trigger validation
            {
                "Project ID": "TD-FAK-01",
                "Funding Source Type": "Towns Fund",
                "Funding Source Name": "funding CDEL",
                "Spend for Reporting Period": 0,
            },
            {
                "Project ID": "TD-FAK-01",
                "Funding Source Type": "Towns Fund",
                "Funding Source Name": "funding RDEL",
                "Spend for Reporting Period": 123,
            },
            # Over spent but contractually committed, won't trigger validation
            {
                "Project ID": "TD-FAK-02",
                "Funding Source Type": "Towns Fund",
                "Funding Source Name": "funding that is contractually committed",
                "Spend for Reporting Period": 124,
            },
            # Project 2 over spent but not Towns Fund source, won't trigger validation
            {
                "Project ID": "TD-FAK-02",
                "Funding Source Type": "Other Funding",
                "Funding Source Name": "CDEL",
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

    assert not failures


def test_validate_funding_spent_skipped_if_non_numeric_data(mocker, allocated_funding):
    mocker.patch(
        "core.validation.towns_fund.fund_specific_validation.round_4.validate.FUNDING_ALLOCATION",
        allocated_funding,
    )
    funding_df = pd.DataFrame(
        data=[
            # Overspent at the programme level sum of all three project spend
            # Project 1
            {
                "Project ID": "HS-FAK-01",
                "Funding Source Type": "Towns Fund",
                "Funding Source Name": "funding CDEL",
                "Spend for Reporting Period": 1,
            },
            {
                "Project ID": "HS-FAK-01",
                "Funding Source Type": "Towns Fund",
                "Funding Source Name": "funding CDEL",
                "Spend for Reporting Period": "Non-numeric value",  # non numeric
            },
        ]
    )

    workbook = {
        "Programme_Ref": pd.DataFrame([{"Programme ID": "HS-FAK", "FundType_ID": "HS"}]),
        "Project Details": pd.DataFrame([{"Project ID": "HS-FAK-01"}]),
        "Funding": funding_df,
    }

    failures = validate_funding_spent(workbook)

    assert failures is None


def test_validate_funding_profiles_funding_secured_not_null():
    funding_df = pd.DataFrame(
        index=[47, 48, 49, 49],
        data=[
            # Secured is NA but funding is not from a custom source
            {
                "Project ID": "TD-ABC-01",
                "Funding Source Type": "Towns Fund",
                "Funding Source Name": PRE_DEFINED_FUNDING_SOURCES[0],
                "Secured": pd.NA,
            },
            # Secured is valid and funding is from a custom source
            {
                "Project ID": "TD-ABC-01",
                "Funding Source Type": "Other Funding Source Type",
                "Funding Source Name": "Some Other Funding Source",
                "Secured": "Yes",
            },
            # Secured is null, custom source
            {
                "Project ID": "TD-ABC-01",
                "Funding Source Type": "Other Funding Source Type",
                "Funding Source Name": "Some Other Funding Source",
                "Secured": pd.NA,
            },
            # Secured is null, custom source (duplicate index, should only produce one Failure)
            {
                "Project ID": "TD-ABC-01",
                "Funding Source Type": "Other Funding Source Type",
                "Funding Source Name": "Some Other Funding Source",
                "Secured": pd.NA,
            },
        ],
    )
    workbook = {"Funding": funding_df}

    failures = validate_funding_profiles_funding_secured_not_null(workbook)

    assert failures == [
        GenericFailure(
            table="Funding",
            section="Project Funding Profiles - Project 1",
            column="Secured",
            message="The cell is blank but is required.",
            row_index=49,
        )
    ]


def test_validate_psi_funding_not_negative():
    psi_df = pd.DataFrame(
        index=[48, 49, 49],
        data=[
            {
                "Private Sector Funding Required": -100,
                "Private Sector Funding Secured": 0,
            },
            {
                "Private Sector Funding Required": 0,
                "Private Sector Funding Secured": 0,
            },
            {
                "Private Sector Funding Required": -1,
                "Private Sector Funding Secured": -2,
            },
        ],
    )
    workbook = {"Private Investments": psi_df}

    failures = validate_psi_funding_not_negative(workbook)

    assert failures == [
        GenericFailure(
            table="Private Investments",
            section="Private Sector Investment",
            column="Private Sector Funding Required",
            message="You’ve entered a negative number. Enter a positive number.",
            row_index=48,
        ),
        GenericFailure(
            table="Private Investments",
            section="Private Sector Investment",
            column="Private Sector Funding Required",
            message="You’ve entered a negative number. Enter a positive number.",
            row_index=49,
        ),
        GenericFailure(
            table="Private Investments",
            section="Private Sector Investment",
            column="Private Sector Funding Secured",
            message="You’ve entered a negative number. Enter a positive number.",
            row_index=49,
        ),
    ]


def test_validate_psi_funding_not_negative_with_strings():
    psi_df = pd.DataFrame(
        index=[48, 49, 49],
        data=[
            {
                "Private Sector Funding Required": "invalid string",
                "Private Sector Funding Secured": 0,
            },
            {
                "Private Sector Funding Required": 0,
                "Private Sector Funding Secured": 0,
            },
            {
                "Private Sector Funding Required": 0,
                "Private Sector Funding Secured": "invalid string",
            },
        ],
    )
    workbook = {"Private Investments": psi_df}

    failures = validate_psi_funding_not_negative(workbook)

    assert failures is None


def test_validate_postcodes():
    project_detail_df = pd.DataFrame(
        index=[7, 8, 9, 10, 11, 12, 13, 14],
        data=[
            # Single postcode
            {
                "Locations": " AB1 2CD ",
                "Postcodes": "AB1 2CD",
            },
            # Comma seperated list
            {
                "Locations": "EF3 4GH IJ5 6KL KL7 8MN",
                "Postcodes": "EF3 4GH, IJ5 6KL, KL7 8MN",
            },
            # Space seperated list
            {
                "Locations": "EF3 4GH IJ5 6KL KL7 8MN",
                "Postcodes": "EF3 4GH IJ5 6KL KL7 8MN",
            },
            # Dash seperated list
            {
                "Locations": "EF3 4GH IJ5 6KL KL7 8MN",
                "Postcodes": "EF3 4GH - IJ5 6KL - KL7 8MN",
            },
            # Blank cell - will not be picked up
            {
                "Locations": pd.NA,
                "Postcodes": "",
            },
            # Locations value, but blank postcode
            {
                "Locations": "NOT A POSTCODE",
                "Postcodes": "",
            },
            # Not postcode format
            {
                "Locations": "NOT A POSTCODE",
                "Postcodes": "NOT A POSTCODE",
            },
            # Incorrect postcode - starts with a number
            {
                "Locations": "12A 2CD",
                "Postcodes": "12A 2CD",
            },
        ],
    )
    workbook = {"Project Details": project_detail_df}

    failures = validate_postcodes(workbook)

    assert failures == [
        GenericFailure(
            table="Project Details",
            section="Project Details",
            column="Postcodes",
            message="You entered an invalid postcode. Enter a full UK postcode, for example SW1A 2AA.",
            row_index=12,
        ),
        GenericFailure(
            table="Project Details",
            section="Project Details",
            column="Postcodes",
            message="You entered an invalid postcode. Enter a full UK postcode, for example SW1A 2AA.",
            row_index=13,
        ),
        GenericFailure(
            table="Project Details",
            section="Project Details",
            column="Postcodes",
            message="You entered an invalid postcode. Enter a full UK postcode, for example SW1A 2AA.",
            row_index=14,
        ),
    ]


def test_validate_postcodes_success():
    project_detail_df = pd.DataFrame(
        index=[7, 8, 9, 10, 11, 12, 13, 14],
        data=[
            # Single postcode
            {
                "Locations": "AB1 2CD ",
                "Postcodes": "AB1 2CD",
            },
        ],
    )
    workbook = {"Project Details": project_detail_df}

    failures = validate_postcodes(workbook)

    assert failures == []


def test_validate_funding_questions_success():
    workbook = {
        "Funding Questions": pd.DataFrame(
            data=[
                {
                    "Question": "Beyond these three funding types, have you received any payments for specific "
                    "projects?",
                    "Indicator": pd.NA,
                    "Response": "Yes",
                },
                {
                    "Question": "Please confirm whether the amount utilised represents your entire allocation",
                    "Indicator": "TD 5% CDEL Pre-Payment\n(Towns Fund FAQs p.46 - 49)",
                    "Response": "Yes",
                },
                {
                    "Question": "Please describe when funding was utilised and, if applicable, when any remaining "
                    "funding will be utilised",
                    "Indicator": "TD Accelerated Funding",
                    "Response": "Value",
                },
                {
                    "Question": "Please explain in detail how the funding has, or will be, utilised",
                    "Indicator": "TD RDEL Capacity Funding",
                    "Response": "Value",
                },
                {
                    "Question": "Please indicate how much of your allocation has been utilised (in £s)",
                    "Indicator": "TD RDEL Capacity Funding",
                    "Response": "1",
                },
                {
                    "Question": "Please select the option that best describes how the funding was, or will be, "
                    "utilised",
                    "Indicator": "TD RDEL Capacity Funding",
                    "Response": "Programme only",
                },
            ]
        )
    }
    failures = validate_funding_questions(workbook)
    assert not failures


def test_validate_funding_questions_dropdown_failure():
    workbook = {
        "Funding Questions": pd.DataFrame(
            index=[45, 67],
            data=[
                {
                    "Question": "Beyond these three funding types, have you received any payments for specific "
                    "projects?",
                    "Indicator": pd.NA,
                    "Response": "Invalid Dropdown Value",
                },
                {
                    "Question": "Please confirm whether the amount utilised represents your entire allocation",
                    "Indicator": "TD 5% CDEL Pre-Payment\n(Towns Fund FAQs p.46 - 49)",
                    "Response": "Invalid Dropdown Value",
                },
            ],
        )
    }
    failures = validate_funding_questions(workbook)
    assert failures and len(failures) == 2
    assert [failure.message for failure in failures] == [msgs.DROPDOWN, msgs.DROPDOWN]  # assert both dropdown
    assert [failure.row_index for failure in failures] == [45, 67]  # assert indexes are correct
    assert failures[0].column == "All Columns"  # assert that NA indicator causes "All Columns"


def test_validate_funding_questions_dropdown():
    workbook = {
        "Funding Questions": pd.DataFrame(
            data=[
                {
                    "Question": "Please confirm whether the amount utilised represents your entire allocation",
                    "Indicator": "TD 5% CDEL Pre-Payment\n(Towns Fund FAQs p.46 - 49)",
                    "Response": "",
                },
                {
                    "Question": "Please describe when funding was utilised and, if applicable, when any remaining "
                    "funding will be utilised",
                    "Indicator": "TD Accelerated Funding",
                    "Response": pd.NA,
                },
            ]
        )
    }
    failures = validate_funding_questions(workbook)
    assert failures and len(failures) == 2
    assert [failure.message for failure in failures] == [msgs.BLANK, msgs.BLANK]  # assert both blank


def test_validate_funding_questions_numerical_failure():
    workbook = {
        "Funding Questions": pd.DataFrame(
            data=[
                {
                    "Question": "Please indicate how much of your allocation has been utilised (in £s)",
                    "Indicator": "TD RDEL Capacity Funding",
                    "Response": "Not a number",
                },
            ]
        )
    }
    failures = validate_funding_questions(workbook)
    assert failures and len(failures) == 1
    assert [failure.message for failure in failures] == [msgs.WRONG_TYPE_NUMERICAL]


def test_validate_current_project_progress_success_with_no_delay():
    project_progress_df = pd.DataFrame(
        index=[21],
        data=[
            {
                "Leading Factor of Delay": "",
                "Project Delivery Status": StatusEnum.COMPLETED,
                "Current Project Delivery Stage": "",
                "Most Important Upcoming Comms Milestone": "",
                "Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)": "",
            }
        ],
    )

    workbook = {"Project Progress": project_progress_df}

    failures = validate_project_progress(workbook)

    assert failures == []


def test_validate_current_project_progress_success_with_no_delay_but_incomplete():
    project_progress_df = pd.DataFrame(
        index=[21],
        data=[
            {
                "Leading Factor of Delay": "",
                "Project Delivery Status": StatusEnum.ONGOING_ON_TRACK,
                "Current Project Delivery Stage": "almost complete",
                "Most Important Upcoming Comms Milestone": "announcement",
                "Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)": "Mar-22",
            }
        ],
    )

    workbook = {"Project Progress": project_progress_df}

    failures = validate_project_progress(workbook)

    assert failures == []


def test_validate_project_progress_leading_success_with_delay():
    project_details_df = pd.DataFrame(
        data=[
            # Project 1: "Delayed" with delay value
            {
                "Project Delivery Status": StatusEnum.ONGOING_DELAYED,
                "Leading Factor of Delay": "some delay",
                "Current Project Delivery Stage": "almost complete",
                "Most Important Upcoming Comms Milestone": "announcement",
                "Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)": "Mar-22",
            },
            # Project 2: "Not started" with delay value
            {
                "Project Delivery Status": StatusEnum.NOT_YET_STARTED,
                "Leading Factor of Delay": "some delay",
                "Current Project Delivery Stage": "almost complete",
                "Most Important Upcoming Comms Milestone": "announcement",
                "Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)": "Mar-22",
            },
        ]
    )
    workbook = {"Project Progress": project_details_df}

    failures = validate_project_progress(workbook)

    assert failures == []


def test_validate_project_progress_current_project_delivery_status_failure():
    project_progress_df = pd.DataFrame(
        index=[21],
        data=[
            {
                "Leading Factor of Delay": "funding shortfall",
                "Project Delivery Status": StatusEnum.NOT_YET_STARTED,
                "Current Project Delivery Stage": "",
                "Most Important Upcoming Comms Milestone": "",
                "Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)": "",
            }
        ],
    )

    workbook = {"Project Progress": project_progress_df}

    failures = validate_project_progress(workbook)

    assert failures == [
        GenericFailure(
            table="Project Progress",
            section="Projects Progress Summary",
            column="Current Project Delivery Stage",
            message="The cell is blank but is required for incomplete projects.",
            row_index=21,
        ),
    ]


def test_validate_project_progress_leading_factor_of_delay_not_yet_started_failure():
    project_details_df = pd.DataFrame(
        data=[
            # Project 1: "Not yet started" with no delay value
            {
                "Project Delivery Status": StatusEnum.NOT_YET_STARTED,
                "Leading Factor of Delay": "",
                "Current Project Delivery Stage": StatusEnum.COMPLETED,
                "Most Important Upcoming Comms Milestone": "something big",
                "Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)": "Mar-22",
            },
            # Project 2: "Completed" with no delay value
            {
                "Project Delivery Status": StatusEnum.COMPLETED,
                "Leading Factor of Delay": "",  # no delay
                "Current Project Delivery Stage": StatusEnum.COMPLETED,
                "Most Important Upcoming Comms Milestone": "something big",
                "Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)": "Mar-22",
            },
        ]
    )
    workbook = {"Project Progress": project_details_df}

    failures = validate_project_progress(workbook)

    assert failures == [
        GenericFailure(
            table="Project Progress",
            section="Projects Progress Summary",
            column="Leading Factor of Delay",
            message=msgs.BLANK,
            row_index=0,
        )
    ]


def test_validate_sign_off_success(valid_workbook_round_four):
    failures = validate_sign_off(valid_workbook_round_four)

    assert failures == []


def test_validate_sign_off_failure(invalid_workbook_round_four):
    failures = validate_sign_off(invalid_workbook_round_four)

    assert failures == [
        GenericFailure(table="Review & Sign-Off", section="-", cell_index="C16", message=msgs.BLANK),
        GenericFailure(table="Review & Sign-Off", section="-", cell_index="C18", message=msgs.BLANK),
        GenericFailure(table="Review & Sign-Off", section="-", cell_index="C8", message=msgs.BLANK),
    ]
