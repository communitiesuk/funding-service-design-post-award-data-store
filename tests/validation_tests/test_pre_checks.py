import pandas as pd
import pytest

import core.validation.failures.user as uf
import core.validation.messages as msgs
from core.const import TF_PLACE_NAMES_TO_ORGANISATIONS
from core.exceptions import ValidationError
from core.validation.failures.user import WrongInputFailure
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
        "TD",
        {"TD", "HS"},
    )
    assert details_dict["Place Name"] == (
        "Newark",
        set(TF_PLACE_NAMES_TO_ORGANISATIONS.keys()),
    )
    assert details_dict["Place Name vs Fund Type"] == ("TD", {"TD"})


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
        "TD",
        {"TD", "HS"},
    )
    assert details_dict["Place Name"] == (
        "Newark",
        set(TF_PLACE_NAMES_TO_ORGANISATIONS.keys()),
    )


def test_extract_round_four_submission_details_blank_place_name(valid_workbook_round_four, mocker):
    valid_workbook_round_four["2 - Project Admin"][4].iloc[6] = ""

    details_dict = extract_submission_details(valid_workbook_round_four, 4, place_names=("Newark",))

    assert details_dict["Place Name"] == (
        "",
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
    assert isinstance(failures[0], uf.WrongInputFailure)

    valid_submission_details["Reporting Period"] = (
        "Invalid Reporting Period",
        {"1 October 2022 to 31 March 2023"},
    )
    failures = pre_transformation_check(valid_submission_details)
    assert len(failures) == 2
    assert isinstance(failures[1], uf.WrongInputFailure)

    valid_submission_details["Fund Type"] = (
        "Invalid Fund Type",
        {"TD", "HS"},
    )
    failures = pre_transformation_check(valid_submission_details)
    assert len(failures) == 3
    assert isinstance(failures[2], uf.WrongInputFailure)

    valid_submission_details["Place Name"] = (
        "",
        set(TF_PLACE_NAMES_TO_ORGANISATIONS.keys()),
    )
    failures = pre_transformation_check(valid_submission_details)
    assert len(failures) == 4
    assert isinstance(failures[3], uf.WrongInputFailure)

    valid_submission_details["Invalid Sheets"] = ["1 - Start Here"]
    failures = pre_transformation_check(valid_submission_details)
    assert len(failures) == 1
    assert isinstance(failures[0], uf.WrongInputFailure)

    valid_submission_details["Missing Sheets"] = ["1 - Start Here"]
    failures = pre_transformation_check(valid_submission_details)
    assert len(failures) == 1
    assert isinstance(failures[0], uf.WrongInputFailure)


def test_place_name_is_valid(valid_submission_details):
    valid_submission_details["Place Name"] = (
        "Not in the dropdown",
        ("Place Name", set(TF_PLACE_NAMES_TO_ORGANISATIONS.keys())),
    )
    failures = pre_transformation_check(valid_submission_details)
    assert len(failures) == 1
    assert isinstance(failures[0], uf.WrongInputFailure)


def test_place_name_is_null(valid_submission_details):
    valid_submission_details["Place Name"] = (
        "",
        ("Place Name", set(TF_PLACE_NAMES_TO_ORGANISATIONS.keys())),
    )
    failures = pre_transformation_check(valid_submission_details)
    assert len(failures) == 1
    assert isinstance(failures[0], uf.WrongInputFailure)


def test_place_name_has_correct_fund_type(valid_submission_details):
    valid_submission_details["Place Name vs Fund Type"] = (
        "TD",
        {"HS"},
    )
    failures = pre_transformation_check(valid_submission_details)
    assert len(failures) == 1
    assert isinstance(failures[0], uf.WrongInputFailure)


def test_place_name_has_correct_fund_type_not_raised(valid_submission_details):
    valid_submission_details["Place Name"] = (
        "",
        ("Place Name", set(TF_PLACE_NAMES_TO_ORGANISATIONS.keys())),
    )
    valid_submission_details["Place Name vs Fund Type"] = (
        "TD",
        {"HS"},
    )
    failures = pre_transformation_check(valid_submission_details)
    assert len(failures) == 1
    assert isinstance(failures[0], uf.WrongInputFailure)
    assert failures[0].value_descriptor == "Place Name"


def test_unauthorised_submission():
    unauthorised_failure_dict = {"Unauthorised Place Name": ("Newark", ("Wigan",))}
    failures = pre_transformation_check(unauthorised_failure_dict)
    assert len(failures) == 1
    assert isinstance(failures[0], uf.UnauthorisedSubmissionFailure)


def test_validate_sign_off_success(valid_workbook_round_four):
    failures = validate_sign_off(valid_workbook_round_four)

    assert failures == []


def test_validate_sign_off_failure(invalid_workbook_round_four):
    failures = validate_sign_off(invalid_workbook_round_four)

    assert failures == [
        uf.GenericFailure(sheet="Review & Sign-Off", section="-", cell_index="C16", message=msgs.BLANK),
        uf.GenericFailure(sheet="Review & Sign-Off", section="-", cell_index="C18", message=msgs.BLANK),
        uf.GenericFailure(sheet="Review & Sign-Off", section="-", cell_index="C8", message=msgs.BLANK),
    ]


def test_full_pre_transformation_validation_pipeline_success(valid_workbook_round_four):
    validation_errors = validate_before_transformation(valid_workbook_round_four, 4, ["Newark"])
    assert validation_errors is None


def test_full_pre_transformation_validation_pipeline_historical_rounds():
    workbook = {"Sheet": pd.DataFrame()}
    validation_errors = validate_before_transformation(workbook, 1, None)
    assert validation_errors is None
    validation_errors = validate_before_transformation(workbook, 2, None)
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


@pytest.fixture
def mocked_project_admin_sheet(valid_workbook_round_four, request):
    valid_workbook_round_four["2 - Project Admin"][4] = [
        "",
        "",
        "",
        "",
        "",
        request.param["fund"],
        request.param["place"],
        "",
        "",
    ]
    return valid_workbook_round_four


@pytest.mark.parametrize(
    "mocked_project_admin_sheet, expected",
    [
        (  # Newark is only a Town_Deal and so cannot be submitted as a Future_High_Street_Fund
            {"fund": "Future_High_Street_Fund", "place": "Newark"},
            [
                WrongInputFailure(
                    value_descriptor="Place Name vs Fund Type",
                    entered_value="HS",
                    expected_values={"TD"},
                )
            ],
        ),
        (
            {"fund": "Future_High_Street_Fund", "place": ""},
            [
                WrongInputFailure(
                    value_descriptor="Place Name",
                    entered_value="",
                    expected_values=TF_PLACE_NAMES_TO_ORGANISATIONS.keys(),
                )
            ],
        ),
        (
            {"fund": "", "place": "Newark"},
            [
                WrongInputFailure(
                    value_descriptor="Fund Type",
                    entered_value="",
                    expected_values={"HS", "TD"},
                )
            ],
        ),
    ],
    indirect=["mocked_project_admin_sheet"],
)
def test_full_pre_transformation_validation_pipeline_failure_place_vs_fund(mocked_project_admin_sheet, expected):
    with pytest.raises(ValidationError) as e:
        validate_before_transformation(mocked_project_admin_sheet, 4, ["Newark"])
    assert e.value.validation_failures == expected
