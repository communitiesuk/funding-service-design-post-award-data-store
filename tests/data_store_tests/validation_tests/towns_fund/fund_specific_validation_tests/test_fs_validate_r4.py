import pandas as pd
import pytest

from data_store.const import StatusEnum, YesNoEnum
from data_store.messaging.tf_messaging import TFMessages as msgs
from data_store.validation.towns_fund.fund_specific_validation.fs_validate_r4 import (
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
        "data_store.validation.towns_fund.fund_specific_validation.fs_validate_r4.validate_sign_off",
        return_value=[],
    )
    functions_to_mock = [
        "data_store.validation.towns_fund.fund_specific_validation.fs_validate_r4.validate_project_risks",
        "data_store.validation.towns_fund.fund_specific_validation.fs_validate_r4.validate_programme_risks",
        "data_store.validation.towns_fund.fund_specific_validation.fs_validate_r4"
        ".validate_funding_profiles_funding_source_enum",
        "data_store.validation.towns_fund.fund_specific_validation.fs_validate_r4"
        ".validate_funding_profiles_at_least_one_other_funding_source_fhsf",
        "data_store.validation.towns_fund.fund_specific_validation.fs_validate_r4.validate_psi_funding_gap",
        "data_store.validation.towns_fund.fund_specific_validation.fs_validate_r4.validate_locations",
        "data_store.validation.towns_fund.fund_specific_validation.fs_validate_r4.validate_funding_spent",
        "data_store.validation.towns_fund.fund_specific_validation.fs_validate_r4"
        ".validate_funding_profiles_funding_secured_not_null",
        "data_store.validation.towns_fund.fund_specific_validation.fs_validate_r4.validate_postcodes",
        "data_store.validation.towns_fund.fund_specific_validation.fs_validate_r4.validate_psi_funding_not_negative",
        "data_store.validation.towns_fund.fund_specific_validation.fs_validate_r4.validate_funding_questions",
        "data_store.validation.towns_fund.fund_specific_validation.fs_validate_r4.validate_project_progress",
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
        "data_store.validation.towns_fund.fund_specific_validation.fs_validate_r4.validate_project_risks",
        return_value=[mocked_failure],
    )
    mocker.patch(
        "data_store.validation.towns_fund.fund_specific_validation.fs_validate_r4.validate_programme_risks",
        return_value=[mocked_failure],
    )
    mocker.patch(
        "data_store.validation.towns_fund.fund_specific_validation.fs_validate_r4.validate_sign_off",
        return_value=[],
    )

    mock_workbook = {"Sheet 1": pd.DataFrame()}
    failures = validate(mock_workbook, original_workbook={}, reporting_round=4)

    assert failures == [mocked_failure, mocked_failure]


def test_validate_success(validation_functions_success_mock):
    mock_workbook = {"Sheet 1": pd.DataFrame()}
    failures = validate(mock_workbook, original_workbook={}, reporting_round=4)
    assert failures == []


def test_validate_project_risks_returns_correct_failure():
    # project 1 completed, no risk = pass
    project_1 = {"project_id": "TD-ABC-01"}
    project_1_progress = {"project_id": "TD-ABC-01", "delivery_status": StatusEnum.COMPLETED}

    # project 2 ongoing, risk = pass
    project_2 = {"project_id": "TD-ABC-02"}
    project_2_progress = {"project_id": "TD-ABC-02", "delivery_status": StatusEnum.ONGOING_ON_TRACK}
    project_2_risk = {"project_id": "TD-ABC-02"}

    # project 3 ongoing, no risk = fail
    project_3 = {"project_id": "TD-ABC-03"}
    project_3_progress = {"project_id": "TD-ABC-03", "delivery_status": StatusEnum.ONGOING_ON_TRACK}

    # programme risk
    programme_risk = {"project_id": pd.NA, "programme_id": "TD-ABC"}

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
            column="risk_name",
            message=msgs.PROJECT_RISKS,
            row_index=37,
        )
    ]


def test_validate_project_risks_returns_correct_failure_no_risks():
    # 3 ongoing projects
    project_progress_df = pd.DataFrame(
        data=[
            {"project_id": "TD-ABC-01", "delivery_status": StatusEnum.ONGOING_ON_TRACK},
            {"project_id": "TD-ABC-03", "delivery_status": StatusEnum.ONGOING_ON_TRACK},
            {"project_id": "TD-ABC-04", "delivery_status": StatusEnum.ONGOING_ON_TRACK},
        ]
    )
    # 3 projects
    project_details_df = pd.DataFrame(
        data=[{"project_id": "TD-ABC-01"}, {"project_id": "TD-ABC-03"}, {"project_id": "TD-ABC-04"}]
    )
    # Risk Register contains no risks at all
    risk_register_df = pd.DataFrame(columns=["project_id"])
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
            column="risk_name",
            message=msgs.PROJECT_RISKS,
            row_index=21,
        ),
        GenericFailure(
            table="RiskRegister",
            section="Project Risks - Project 2",
            column="risk_name",
            message=msgs.PROJECT_RISKS,
            row_index=29,
        ),
        GenericFailure(
            table="RiskRegister",
            section="Project Risks - Project 3",
            column="risk_name",
            message=msgs.PROJECT_RISKS,
            row_index=37,
        ),
    ]


def test_validate_project_risks_returns_no_failure():
    project_details_df = pd.DataFrame(data=[{"project_id": "TD-ABC-01"}])
    project_progress_df = pd.DataFrame(
        data=[{"project_id": "TD-ABC-01", "delivery_status": StatusEnum.ONGOING_ON_TRACK}]
    )
    risk_register_df = pd.DataFrame(data=[{"project_id": "TD-ABC-01"}])
    workbook = {
        "Project Details": project_details_df,
        "Project Progress": project_progress_df,
        "RiskRegister": risk_register_df,
    }

    failures = validate_project_risks(workbook)

    assert failures is None


def test_validate_programme_risks_returns_correct_failure():
    # simulates risks containing 1 project risk and 0 programme risks - at least 1 programme risk is required
    risk_register_df = pd.DataFrame(data=[{"project_id": "TD-ABC-01", "programme_id": pd.NA}])
    workbook = {"RiskRegister": risk_register_df}

    failures = validate_programme_risks(workbook)

    assert failures == [
        GenericFailure(
            table="RiskRegister",
            section="Programme Risks",
            column="risk_name",
            message=msgs.PROGRAMME_RISKS,
            row_index=10,
        )
    ]


def test_validate_programme_risks_returns_correct_failure_no_risks():
    # Risk Register contains no risks at all
    risk_register_df = pd.DataFrame(columns=["programme_id"])
    workbook = {"RiskRegister": risk_register_df}

    failures = validate_programme_risks(workbook)

    assert failures == [
        GenericFailure(
            table="RiskRegister",
            section="Programme Risks",
            column="risk_name",
            message=msgs.PROGRAMME_RISKS,
            row_index=10,
        )
    ]


def test_validate_programme_risks_returns_no_failure():
    # simulates risks containing 3 programme level risks
    risk_register_df = pd.DataFrame(
        data=[
            {"project_id": pd.NA, "programme_id": "TD-ABC"},
            {"project_id": pd.NA, "programme_id": "TD-ABC"},
            {"project_id": pd.NA, "programme_id": "TD-ABC"},
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
                "project_id": "TD-ABC-01",
                "spend_type": PRE_DEFINED_FUNDING_SOURCES[0],
                "funding_source": "Towns Fund",
            },
            # Invalid "Other Funding Source"
            {
                "project_id": "TD-ABC-01",
                "spend_type": "Invalid Funding Source Type",
                "funding_source": "Some Other Funding Source",
            },
        ],
    )
    workbook = {"Funding": funding_df}

    failures = validate_funding_profiles_funding_source_enum(workbook)

    assert failures == [
        GenericFailure(
            table="Funding",
            section="Project Funding Profiles - Project 1",
            column="spend_type",
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
                "project_id": "TD-ABC-01",
                "spend_type": "Invalid Funding Source Type 1",
                "funding_source": "Some Other Funding Source",
            },
            # Invalid "Other Funding Source" 1
            {
                "project_id": "TD-ABC-01",
                "spend_type": "Invalid Funding Source Type 1",
                "funding_source": "Some Other Funding Source",
            },
            # Invalid "Other Funding Source" 2
            {
                "project_id": "TD-ABC-03",
                "spend_type": "Invalid Funding Source Type 2",
                "funding_source": "Some Other Funding Source",
            },
        ],
    )
    workbook = {"Funding": funding_df}

    failures = validate_funding_profiles_funding_source_enum(workbook)

    assert failures == [
        GenericFailure(
            table="Funding",
            section="Project Funding Profiles - Project 1",
            column="spend_type",
            message=msgs.DROPDOWN,
            row_index=48,
        ),
        GenericFailure(
            table="Funding",
            section="Project Funding Profiles - Project 3",
            column="spend_type",
            message=msgs.DROPDOWN,
            row_index=106,
        ),
    ]


def test_validate_funding_profiles_funding_source_success():
    funding_df = pd.DataFrame(
        data=[
            # Pre-defined Funding Source
            {
                "project_id": "TD-ABC-01",
                "spend_type": PRE_DEFINED_FUNDING_SOURCES[0],
                "funding_source": "Towns Fund",
            },
            # Valid "Other Funding Source"
            {
                "project_id": "TD-ABC-01",
                "spend_type": "Local Authority",  # valid Funding Source Type
                "funding_source": "Some Other Funding Source",
            },
        ]
    )
    workbook = {"Funding": funding_df}

    failures = validate_funding_profiles_funding_source_enum(workbook)

    assert failures is None


def test_validate_funding_profiles_at_least_one_other_funding_source_fhsf_success_non_fhsf():
    programme_ref_df = pd.DataFrame(data=[{"fund_type_id": "TD"}])
    workbook = {"Programme_Ref": programme_ref_df}

    failures = validate_funding_profiles_at_least_one_other_funding_source_fhsf(workbook)

    assert failures is None


def test_validate_funding_profiles_at_least_one_other_funding_source_fhsf_success():
    programme_ref_df = pd.DataFrame(data=[{"fund_type_id": "HS"}])
    funding_df = pd.DataFrame(
        data=[
            # Pre-defined Funding Source
            {
                "spend_type": PRE_DEFINED_FUNDING_SOURCES[0],
                "funding_source": "Towns Fund",
            },
            # "Other Funding Source"
            {
                "spend_type": "Some Other Funding Type",
                "funding_source": "Some Other Funding Source",
            },
        ]
    )

    workbook = {"Programme_Ref": programme_ref_df, "Funding": funding_df}

    failures = validate_funding_profiles_at_least_one_other_funding_source_fhsf(workbook)

    assert failures is None


def test_validate_funding_profiles_at_least_one_other_funding_source_fhsf_failure():
    programme_ref_df = pd.DataFrame(data=[{"fund_type_id": "HS"}])
    funding_df = pd.DataFrame(
        data=[
            # Pre-defined Funding Source
            {
                "spend_type": PRE_DEFINED_FUNDING_SOURCES[0],
                "funding_source": "Towns Fund",
            },
        ]
    )

    workbook = {"Programme_Ref": programme_ref_df, "Funding": funding_df}

    failures = validate_funding_profiles_at_least_one_other_funding_source_fhsf(workbook)

    assert failures == [
        GenericFailure(
            table="Funding",
            section="Project Funding Profiles",
            column="spend_type",
            message=msgs.MISSING_OTHER_FUNDING_SOURCES,
            row_index=None,
        )
    ]


def test_validate_psi_funding_gap():
    psi_df = pd.DataFrame(
        index=[10],
        data=[
            {
                "private_sector_funding_required": 100,
                "private_sector_funding_secured": 0,
                "additional_comments": pd.NA,
            },
        ],
    )
    workbook = {"Private Investments": psi_df}

    failures = validate_psi_funding_gap(workbook)

    assert failures == [
        GenericFailure(
            table="Private Investments",
            section="Private Sector Investment",
            column="additional_comments",
            message=msgs.BLANK_PSI,
            row_index=10,
        )
    ]


def test_validate_psi_funding_gap_success():
    psi_df = pd.DataFrame(
        data=[
            {
                "private_sector_funding_required": [100, 100],
                "private_sector_funding_secured": [0, 100],
                "additional_comments": ["Comment", pd.NA],
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
            # Project 1: Single - valid locations and lat_long data
            {
                "location_multiplicity": "Multiple",
                "gis_provided": YesNoEnum.YES,
                "locations": "AB1 2CD",
                "lat_long": "Test Coords",
            },
            # Project 2: Multiple - valid locations, lat_long data and gis_provided data
            {
                "location_multiplicity": "Single",
                "gis_provided": pd.NA,
                "locations": "AB1 2CD",
                "lat_long": "Test Coords",
            },
            # Project 3: Invalid Single / Multiple - invalid locations, lat_long data and gis_provided data
            # this should not produce failures because the Single / Multiple value is invalid (this is picked up during
            # schema validation)
            {"location_multiplicity": "Invalid Value", "gis_provided": pd.NA, "locations": "", "lat_long": ""},
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
            # Project 1: Multiple - invalid locations and lat_long data
            {
                "location_multiplicity": "Multiple",
                "gis_provided": pd.NA,  # empty failure"
                "locations": pd.NA,  # empty failure
                "lat_long": pd.NA,  # no failure
            },
            # Project 1: Multiple - invalid locations and lat_long data
            {
                "location_multiplicity": "Multiple",
                "gis_provided": pd.NA,  # empty failure"
                "locations": pd.NA,  # empty failure
                "lat_long": pd.NA,  # no failure
            },
            # Project 2: Single - invalid locations, lat_long data and gis_provided data
            {
                "location_multiplicity": "Single",
                "gis_provided": pd.NA,
                "locations": pd.NA,  # empty failure
                "lat_long": pd.NA,  # no failure
            },
            # Project 3: Single - invalid locations, gis_provided data
            {
                "location_multiplicity": "Multiple",
                "gis_provided": "Invalid enum value",  # enum failure
                "locations": "Not empty",
                "lat_long": "Not empty",
            },
        ],
    )
    workbook = {"Project Details": project_details_df}

    failures = validate_locations(workbook)

    assert failures == [
        GenericFailure(
            table="Project Details",
            section="Project Details",
            column="locations",
            message=msgs.BLANK,
            row_index=3,
        ),
        GenericFailure(
            table="Project Details",
            section="Project Details",
            column="locations",
            message=msgs.BLANK,
            row_index=1,
        ),
        GenericFailure(
            table="Project Details",
            section="Project Details",
            column="locations",
            message=msgs.BLANK,
            row_index=2,
        ),
        GenericFailure(
            table="Project Details",
            section="Project Details",
            column="gis_provided",
            message=msgs.BLANK,
            row_index=1,
        ),
        GenericFailure(
            table="Project Details",
            section="Project Details",
            column="gis_provided",
            message=msgs.BLANK,
            row_index=2,
        ),
        GenericFailure(
            table="Project Details",
            section="Project Details",
            column="gis_provided",
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
        "data_store.validation.towns_fund.fund_specific_validation.fs_validate_r4.FUNDING_ALLOCATION",
        allocated_funding,
    )

    funding_df = pd.DataFrame(
        data=[
            # Project 1 over spent will trigger validation CDEL and RDEL
            {
                "project_id": "TD-FAK-01",
                "funding_source": "Towns Fund",
                "spend_type": "funding CDEL",
                "spend_for_reporting_period": 124,
            },
            {
                "project_id": "TD-FAK-01",
                "funding_source": "Towns Fund",
                "spend_type": "funding RDEL",
                "spend_for_reporting_period": 124,
            },
            # Project 3 only towns fund funding, will trigger validation
            {
                "project_id": "TD-FAK-03",
                "funding_source": "Towns Fund",
                "spend_type": "example funding RDEL",
                "spend_for_reporting_period": 124,
            },
            {
                "project_id": "TD-FAK-03",
                "funding_source": "Other funding source",
                "spend_type": "example funding CDEL",
                "spend_for_reporting_period": 124,
            },
        ]
    )

    workbook = {
        "Programme_Ref": pd.DataFrame([{"programme_id": "TD-FAK", "fund_type_id": "TD"}]),
        "Project Details": pd.DataFrame(
            [{"project_id": "TD-FAK-01"}, {"project_id": "TD-FAK-02"}, {"project_id": "TD-FAK-03"}]
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
        "data_store.validation.towns_fund.fund_specific_validation.fs_validate_r4.FUNDING_ALLOCATION",
        allocated_funding,
    )

    funding_df = pd.DataFrame(
        data=[
            # Should not trigger failure for overspending due to floating points being rounded to 2dp
            {
                "project_id": "TD-FAK-01",
                "funding_source": "Towns Fund",
                "spend_type": "funding CDEL",
                "spend_for_reporting_period": 123.0000000001,
            },
        ]
    )

    workbook = {
        "Programme_Ref": pd.DataFrame([{"programme_id": "TD-FAK", "fund_type_id": "TD"}]),
        "Project Details": pd.DataFrame([{"project_id": "TD-FAK-01"}]),
        "Funding": funding_df,
    }

    failures = validate_funding_spent(workbook)

    assert not failures


def test_validate_funding_spent_FHSF(mocker, allocated_funding):
    mocker.patch(
        "data_store.validation.towns_fund.fund_specific_validation.fs_validate_r4.FUNDING_ALLOCATION",
        allocated_funding,
    )

    funding_df = pd.DataFrame(
        data=[
            # Overspent at the programme level sum of all three project spend
            # Project 1
            {
                "project_id": "HS-FAK-01",
                "funding_source": "Towns Fund",
                "spend_type": "funding CDEL",
                "spend_for_reporting_period": 100,
            },
            # Project 2
            {
                "project_id": "HS-FAK-02",
                "funding_source": "Towns Fund",
                "spend_type": "funding RDEL",
                "spend_for_reporting_period": 100,
            },
            # Project 3
            {
                "project_id": "HS-FAK-03",
                "funding_source": "Towns Fund",
                "spend_type": "funding CDEL",
                "spend_for_reporting_period": 100,
            },
        ]
    )

    workbook = {
        "Programme_Ref": pd.DataFrame([{"programme_id": "HS-FAK", "fund_type_id": "HS"}]),
        "Project Details": pd.DataFrame(
            [{"project_id": "HS-FAK-01"}, {"project_id": "HS-FAK-02"}, {"project_id": "HS-FAK-03"}]
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
        "data_store.validation.towns_fund.fund_specific_validation.fs_validate_r4.FUNDING_ALLOCATION",
        allocated_funding,
    )
    funding_df = pd.DataFrame(
        data=[
            # Under spent or exactly as allocated, won't trigger validation
            {
                "project_id": "TD-FAK-01",
                "funding_source": "Towns Fund",
                "spend_type": "funding CDEL",
                "spend_for_reporting_period": 0,
            },
            {
                "project_id": "TD-FAK-01",
                "funding_source": "Towns Fund",
                "spend_type": "funding RDEL",
                "spend_for_reporting_period": 123,
            },
            # Over spent but contractually committed, won't trigger validation
            {
                "project_id": "TD-FAK-02",
                "funding_source": "Towns Fund",
                "spend_type": "funding that is contractually committed",
                "spend_for_reporting_period": 124,
            },
            # Project 2 over spent but not Towns Fund source, won't trigger validation
            {
                "project_id": "TD-FAK-02",
                "funding_source": "Other Funding",
                "spend_type": "CDEL",
                "spend_for_reporting_period": 124,
            },
        ]
    )

    workbook = {
        "Programme_Ref": pd.DataFrame([{"programme_id": "TD-FAK", "fund_type_id": "TD"}]),
        "Project Details": pd.DataFrame(
            [{"project_id": "TD-FAK-01"}, {"project_id": "TD-FAK-02"}, {"project_id": "TD-FAK-03"}]
        ),
        "Funding": funding_df,
    }

    failures = validate_funding_spent(workbook)

    assert not failures


def test_validate_funding_spent_skipped_if_non_numeric_data(mocker, allocated_funding):
    mocker.patch(
        "data_store.validation.towns_fund.fund_specific_validation.fs_validate_r4.FUNDING_ALLOCATION",
        allocated_funding,
    )
    funding_df = pd.DataFrame(
        data=[
            # Overspent at the programme level sum of all three project spend
            # Project 1
            {
                "project_id": "HS-FAK-01",
                "funding_source": "Towns Fund",
                "spend_type": "funding CDEL",
                "spend_for_reporting_period": 1,
            },
            {
                "project_id": "HS-FAK-01",
                "funding_source": "Towns Fund",
                "spend_type": "funding CDEL",
                "spend_for_reporting_period": "Non-numeric value",  # non numeric
            },
        ]
    )

    workbook = {
        "Programme_Ref": pd.DataFrame([{"programme_id": "HS-FAK", "fund_type_id": "HS"}]),
        "Project Details": pd.DataFrame([{"project_id": "HS-FAK-01"}]),
        "Funding": funding_df,
    }

    failures = validate_funding_spent(workbook)

    assert failures is None


def test_validate_funding_profiles_funding_secured_not_null():
    funding_df = pd.DataFrame(
        index=[47, 48, 49, 49],
        data=[
            # secured is NA but funding is not from a custom source
            {
                "project_id": "TD-ABC-01",
                "spend_type": PRE_DEFINED_FUNDING_SOURCES[0],
                "funding_source": "Towns Fund",
                "secured": pd.NA,
            },
            # secured is valid and funding is from a custom source
            {
                "project_id": "TD-ABC-01",
                "spend_type": "Other Funding Source Type",
                "funding_source": "Some Other Funding Source",
                "secured": "Yes",
            },
            # secured is null, custom source
            {
                "project_id": "TD-ABC-01",
                "spend_type": "Other Funding Source Type",
                "funding_source": "Some Other Funding Source",
                "secured": pd.NA,
            },
            # secured is null, custom source (duplicate index, should only produce one Failure)
            {
                "project_id": "TD-ABC-01",
                "spend_type": "Other Funding Source Type",
                "funding_source": "Some Other Funding Source",
                "secured": pd.NA,
            },
        ],
    )
    workbook = {"Funding": funding_df}

    failures = validate_funding_profiles_funding_secured_not_null(workbook)

    assert failures == [
        GenericFailure(
            table="Funding",
            section="Project Funding Profiles - Project 1",
            column="secured",
            message="The cell is blank but is required.",
            row_index=49,
        )
    ]


def test_validate_psi_funding_not_negative():
    psi_df = pd.DataFrame(
        index=[48, 49, 49],
        data=[
            {
                "private_sector_funding_required": -100,
                "private_sector_funding_secured": 0,
            },
            {
                "private_sector_funding_required": 0,
                "private_sector_funding_secured": 0,
            },
            {
                "private_sector_funding_required": -1,
                "private_sector_funding_secured": -2,
            },
        ],
    )
    workbook = {"Private Investments": psi_df}

    failures = validate_psi_funding_not_negative(workbook)

    assert failures == [
        GenericFailure(
            table="Private Investments",
            section="Private Sector Investment",
            column="private_sector_funding_required",
            message="You’ve entered a negative number. Enter a positive number.",
            row_index=48,
        ),
        GenericFailure(
            table="Private Investments",
            section="Private Sector Investment",
            column="private_sector_funding_required",
            message="You’ve entered a negative number. Enter a positive number.",
            row_index=49,
        ),
        GenericFailure(
            table="Private Investments",
            section="Private Sector Investment",
            column="private_sector_funding_secured",
            message="You’ve entered a negative number. Enter a positive number.",
            row_index=49,
        ),
    ]


def test_validate_psi_funding_not_negative_with_strings():
    psi_df = pd.DataFrame(
        index=[48, 49, 49],
        data=[
            {
                "private_sector_funding_required": "invalid string",
                "private_sector_funding_secured": 0,
            },
            {
                "private_sector_funding_required": 0,
                "private_sector_funding_secured": 0,
            },
            {
                "private_sector_funding_required": 0,
                "private_sector_funding_secured": "invalid string",
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
                "locations": " AB1 2CD ",
                "postcodes": "AB1 2CD",
            },
            # Comma seperated list
            {
                "locations": "EF3 4GH IJ5 6KL KL7 8MN",
                "postcodes": "EF3 4GH, IJ5 6KL, KL7 8MN",
            },
            # Space seperated list
            {
                "locations": "EF3 4GH IJ5 6KL KL7 8MN",
                "postcodes": "EF3 4GH IJ5 6KL KL7 8MN",
            },
            # Dash seperated list
            {
                "locations": "EF3 4GH IJ5 6KL KL7 8MN",
                "postcodes": "EF3 4GH - IJ5 6KL - KL7 8MN",
            },
            # Blank cell - will not be picked up
            {
                "locations": pd.NA,
                "postcodes": "",
            },
            # locations value, but blank postcode
            {
                "locations": "NOT A POSTCODE",
                "postcodes": "",
            },
            # Not postcode format
            {
                "locations": "NOT A POSTCODE",
                "postcodes": "NOT A POSTCODE",
            },
            # Incorrect postcode - starts with a number
            {
                "locations": "12A 2CD",
                "postcodes": "12A 2CD",
            },
        ],
    )
    workbook = {"Project Details": project_detail_df}

    failures = validate_postcodes(workbook)

    assert failures == [
        GenericFailure(
            table="Project Details",
            section="Project Details",
            column="postcodes",
            message="You entered an invalid postcode. Enter a full UK postcode, for example SW1A 2AA.",
            row_index=12,
        ),
        GenericFailure(
            table="Project Details",
            section="Project Details",
            column="postcodes",
            message="You entered an invalid postcode. Enter a full UK postcode, for example SW1A 2AA.",
            row_index=13,
        ),
        GenericFailure(
            table="Project Details",
            section="Project Details",
            column="postcodes",
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
                "locations": "AB1 2CD ",
                "postcodes": "AB1 2CD",
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
                    "question": "Beyond these three funding types, have you received any payments for specific "
                    "projects?",
                    "indicator": pd.NA,
                    "response": "Yes",
                },
                {
                    "question": "Please confirm whether the amount utilised represents your entire allocation",
                    "indicator": "TD 5% CDEL Pre-Payment\n(Towns Fund FAQs p.46 - 49)",
                    "response": "Yes",
                },
                {
                    "question": "Please describe when funding was utilised and, if applicable, when any remaining "
                    "funding will be utilised",
                    "indicator": "TD Accelerated Funding",
                    "response": "Value",
                },
                {
                    "question": "Please explain in detail how the funding has, or will be, utilised",
                    "indicator": "TD RDEL Capacity Funding",
                    "response": "Value",
                },
                {
                    "question": "Please indicate how much of your allocation has been utilised (in £s)",
                    "indicator": "TD RDEL Capacity Funding",
                    "response": "1",
                },
                {
                    "question": "Please select the option that best describes how the funding was, or will be, "
                    "utilised",
                    "indicator": "TD RDEL Capacity Funding",
                    "response": "Programme only",
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
                    "question": "Beyond these three funding types, have you received any payments for specific "
                    "projects?",
                    "indicator": pd.NA,
                    "response": "Invalid Dropdown Value",
                },
                {
                    "question": "Please confirm whether the amount utilised represents your entire allocation",
                    "indicator": "TD 5% CDEL Pre-Payment\n(Towns Fund FAQs p.46 - 49)",
                    "response": "Invalid Dropdown Value",
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
                    "question": "Please confirm whether the amount utilised represents your entire allocation",
                    "indicator": "TD 5% CDEL Pre-Payment\n(Towns Fund FAQs p.46 - 49)",
                    "response": "",
                },
                {
                    "question": "Please describe when funding was utilised and, if applicable, when any remaining "
                    "funding will be utilised",
                    "indicator": "TD Accelerated Funding",
                    "response": pd.NA,
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
                    "question": "Please indicate how much of your allocation has been utilised (in £s)",
                    "indicator": "TD RDEL Capacity Funding",
                    "response": "Not a number",
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
                "leading_factor_of_delay": "",
                "delivery_status": StatusEnum.COMPLETED,
                "delivery_stage": "",
                "important_milestone": "",
                "date_of_important_milestone": "",
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
                "leading_factor_of_delay": "",
                "delivery_status": StatusEnum.ONGOING_ON_TRACK,
                "delivery_stage": "almost complete",
                "important_milestone": "announcement",
                "date_of_important_milestone": "Mar-22",
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
                "delivery_status": StatusEnum.ONGOING_DELAYED,
                "leading_factor_of_delay": "some delay",
                "delivery_stage": "almost complete",
                "important_milestone": "announcement",
                "date_of_important_milestone": "Mar-22",
            },
            # Project 2: "Not started" with delay value
            {
                "delivery_status": StatusEnum.NOT_YET_STARTED,
                "leading_factor_of_delay": "some delay",
                "delivery_stage": "almost complete",
                "important_milestone": "announcement",
                "date_of_important_milestone": "Mar-22",
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
                "leading_factor_of_delay": "funding shortfall",
                "delivery_status": StatusEnum.NOT_YET_STARTED,
                "delivery_stage": "",
                "important_milestone": "",
                "date_of_important_milestone": "",
            }
        ],
    )

    workbook = {"Project Progress": project_progress_df}

    failures = validate_project_progress(workbook)

    assert failures == [
        GenericFailure(
            table="Project Progress",
            section="Projects Progress Summary",
            column="delivery_stage",
            message="The cell is blank but is required for incomplete projects.",
            row_index=21,
        ),
    ]


def test_validate_project_progress_leading_factor_of_delay_not_yet_started_failure():
    project_details_df = pd.DataFrame(
        data=[
            # Project 1: "Not yet started" with no delay value
            {
                "delivery_status": StatusEnum.NOT_YET_STARTED,
                "leading_factor_of_delay": "",
                "delivery_stage": StatusEnum.COMPLETED,
                "important_milestone": "something big",
                "date_of_important_milestone": "Mar-22",
            },
            # Project 2: "Completed" with no delay value
            {
                "delivery_status": StatusEnum.COMPLETED,
                "leading_factor_of_delay": "",  # no delay
                "delivery_stage": StatusEnum.COMPLETED,
                "important_milestone": "something big",
                "date_of_important_milestone": "Mar-22",
            },
        ]
    )
    workbook = {"Project Progress": project_details_df}

    failures = validate_project_progress(workbook)

    assert failures == [
        GenericFailure(
            table="Project Progress",
            section="Projects Progress Summary",
            column="leading_factor_of_delay",
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
