import pytest

import core.validation.failures as vf
from core.const import TF_PLACE_NAMES_TO_ORGANISATIONS
from core.exceptions import ValidationError
from core.validation.failures import WrongInputFailure
from core.validation.initial_check import (
    extract_submission_details,
    pre_transformation_check,
    validate_before_transformation,
    validate_sign_off,
)


@pytest.fixture(scope="function", autouse=True)
def mock_form_version_reporting_period(mocker):
    mocker.patch(
        "core.validation.initial_check.GET_FORM_VERSION_AND_REPORTING_PERIOD",
        {
            3: ("Town Deals and Future High Streets Fund Reporting Template (v3.0)", "1 October 2022 to 31 March 2023"),
            4: (
                "Town Deals and Future High Streets Fund Reporting Template (v4.0)",
                "1 April 2023 to 30 September 2023",
            ),
        },
    )


def test_extract_round_three_submission_details(valid_workbook):
    details_dict = extract_submission_details(valid_workbook, 3, place_names=("Newark",))

    assert "Missing Sheets" not in details_dict
    assert details_dict["Form Version"] == (
        "Town Deals and Future High Streets Fund Reporting Template (v3.0)",
        {"Town Deals and Future High Streets Fund Reporting Template (v3.0)"},
    )
    assert details_dict["Reporting Period"] == (
        "1 October 2022 to 31 March 2023",
        {"1 October 2022 to 31 March 2023"},
    )
    assert details_dict["Fund Type"] == (
        "Town_Deal",
        {"Town_Deal", "Future_High_Street_Fund"},
    )
    assert details_dict["Place Name"] == (
        "Newark",
        set(TF_PLACE_NAMES_TO_ORGANISATIONS.keys()),
    )


def test_extract_round_four_submission_details(valid_workbook_round_four, mocker):
    details_dict = extract_submission_details(valid_workbook_round_four, 4, place_names=("Newark",))

    assert details_dict["Form Version"] == (
        "Town Deals and Future High Streets Fund Reporting Template (v4.0)",
        {"Town Deals and Future High Streets Fund Reporting Template (v4.0)"},
    )
    assert details_dict["Reporting Period"] == (
        "1 April 2023 to 30 September 2023",
        {"1 April 2023 to 30 September 2023"},
    )
    assert details_dict["Fund Type"] == (
        "Town_Deal",
        {"Town_Deal", "Future_High_Street_Fund"},
    )
    assert details_dict["Place Name"] == (
        "Newark",
        set(TF_PLACE_NAMES_TO_ORGANISATIONS.keys()),
    )


def test_extract_with_unauthorised_place_name(valid_workbook_round_four):
    unauthorised_place_name_dict = extract_submission_details(valid_workbook_round_four, 4, place_names=("Wigan",))

    assert unauthorised_place_name_dict == {"Unauthorised Place Name": ("Newark", ("Wigan",))}


def test_pre_transformation_check_success(valid_submission_details):
    failures = pre_transformation_check(valid_submission_details)

    assert len(failures) == 0


def test_pre_transformation_check_failures(valid_submission_details):
    valid_submission_details["Form Version"] = (
        "Invalid Form Version",
        {"Town Deals and Future High Streets Fund Reporting Template (v3.0)"},
    )
    failures = pre_transformation_check(valid_submission_details)

    assert len(failures) == 1
    assert isinstance(failures[0], vf.WrongInputFailure)

    valid_submission_details["Reporting Period"] = (
        "Invalid Reporting Period",
        {"1 October 2022 to 31 March 2023"},
    )
    failures = pre_transformation_check(valid_submission_details)
    assert len(failures) == 2
    assert isinstance(failures[1], vf.WrongInputFailure)

    valid_submission_details["Fund Type"] = (
        "Invalid Fund Type",
        {"Town_Deal", "Future_High_Street_Fund"},
    )
    failures = pre_transformation_check(valid_submission_details)
    assert len(failures) == 3
    assert isinstance(failures[2], vf.WrongInputFailure)

    valid_submission_details["Place Name"] = (
        "",
        set(TF_PLACE_NAMES_TO_ORGANISATIONS.keys()),
    )
    failures = pre_transformation_check(valid_submission_details)
    assert len(failures) == 4
    assert isinstance(failures[3], vf.WrongInputFailure)

    valid_submission_details["Invalid Sheets"] = ["1 - Start Here"]
    failures = pre_transformation_check(valid_submission_details)
    assert len(failures) == 1
    assert isinstance(failures[0], vf.InvalidSheetFailure)

    valid_submission_details["Missing Sheets"] = ["1 - Start Here"]
    failures = pre_transformation_check(valid_submission_details)
    assert len(failures) == 1
    assert isinstance(failures[0], vf.EmptySheetFailure)


def test_place_name_is_valid(valid_submission_details):
    valid_submission_details["Place Name"] = (
        "Not in the dropdown",
        ("Place Name", set(TF_PLACE_NAMES_TO_ORGANISATIONS.keys())),
    )
    failures = pre_transformation_check(valid_submission_details)
    assert len(failures) == 1
    assert isinstance(failures[0], vf.WrongInputFailure)


def test_unauthorised_submission():
    unauthorised_failure_dict = {"Unauthorised Place Name": ("Newark", ("Wigan",))}
    failures = pre_transformation_check(unauthorised_failure_dict)
    assert len(failures) == 1
    assert isinstance(failures[0], vf.UnauthorisedSubmissionFailure)


def test_validate_sign_off_success(valid_workbook_round_four):
    failures = validate_sign_off(valid_workbook_round_four)

    assert failures == []


def test_validate_sign_off_failure(invalid_workbook_round_four):
    failures = validate_sign_off(invalid_workbook_round_four)

    assert failures == [
        vf.SignOffFailure(
            tab="Review & Sign-Off",
            section="Section 151 Officer / Chief Finance Officer",
            missing_value="Name",
            sign_off_officer="an S151 Officer or Chief Finance Officer",
        ),
        vf.SignOffFailure(
            tab="Review & Sign-Off",
            section="Town Board Chair",
            missing_value="Role",
            sign_off_officer="a programme SRO",
        ),
        vf.SignOffFailure(
            tab="Review & Sign-Off",
            section="Town Board Chair",
            missing_value="Date",
            sign_off_officer="a programme SRO",
        ),
    ]


def test_full_pre_transformation_validation_pipeline_success(valid_workbook_round_four):
    validation_errors = validate_before_transformation(valid_workbook_round_four, 4, ["Newark"])
    assert validation_errors is None


def test_full_pre_transformation_validation_pipeline_failure(valid_workbook):
    with pytest.raises(ValidationError) as e:
        validate_before_transformation(valid_workbook, 4, ["Newark"])

    assert e.value.validation_failures == [
        WrongInputFailure(
            value_descriptor="Form Version",
            entered_value="Town Deals and Future High Streets Fund Reporting Template (v3.0)",
            expected_values={"Town Deals and Future High Streets Fund Reporting Template (v4.0)"},
        ),
        WrongInputFailure(
            value_descriptor="Reporting Period",
            entered_value="1 October 2022 to 31 March 2023",
            expected_values={"1 April 2023 to 30 September 2023"},
        ),
    ]
