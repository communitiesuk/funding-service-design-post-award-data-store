import pytest

from core.const import TF_PLACE_NAMES_TO_ORGANISATIONS
from core.exceptions import ValidationError
from core.validation.failures.user import (
    UnauthorisedSubmissionFailure,
    WrongInputFailure,
)
from core.validation.pre_transformation_validate import (
    authorisation_validation,
    conflicting_input_validation,
    pre_transformation_validations,
    wrong_input_validation,
)
from core.validation.pre_transformation_validation_schema import TF_ROUND_4


@pytest.fixture
def mocked_start_here_sheet(valid_workbook_round_four, request):
    valid_workbook_round_four["1 - Start Here"][1] = [
        "",
        "",
        "",
        "",
        request.param["reporting_round"],
        "",
        request.param["form_version"],
        "",
        "",
    ]
    return valid_workbook_round_four


@pytest.mark.parametrize(
    "mocked_start_here_sheet, reporting_round, auth",
    [
        (
            {
                "reporting_round": "1 April 2023 to 30 September 2023",
                "form_version": "Town Deals and Future High Streets Fund Reporting Template (v4.3)",
            },
            4,
            {"Place Names": ("Newark",), "Fund Types": ("Town_Deal",)},
        ),
        (
            {
                "reporting_round": "1 April 2023 to 30 September 2023",
                "form_version": "Town Deals and Future High Streets Fund Reporting Template (v4.3)",
            },
            4,
            None,
        ),
        (
            {
                "reporting_round": "1 October 2022 to 31 March 2023",
                "form_version": "Town Deals and Future High Streets Fund Reporting Template (v3.0)",
            },
            3,
            {"Place Names": ("Newark",), "Fund Types": ("Town_Deal",)},
        ),
        ({"reporting_round": "", "form_version": ""}, 2, None),
        ({"reporting_round": "", "form_version": ""}, 1, None),
    ],
    indirect=["mocked_start_here_sheet"],
)
def test_pre_transformation_validations_pipeline_success(
    mocked_start_here_sheet,
    reporting_round,
    auth,
):
    errors = pre_transformation_validations(
        mocked_start_here_sheet,
        reporting_round,
        auth,
    )
    assert errors is None


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
                    entered_value="Future_High_Street_Fund",
                    expected_values=("Town_Deal",),
                )
            ],
        ),
        (
            {"fund": "Future_High_Street_Fund", "place": ""},
            [
                WrongInputFailure(
                    value_descriptor="Place Name",
                    entered_value="",
                    expected_values=tuple(TF_PLACE_NAMES_TO_ORGANISATIONS.keys()),
                )
            ],
        ),
        (
            {"fund": "", "place": "Newark"},
            [
                WrongInputFailure(
                    value_descriptor="Fund Type",
                    entered_value="",
                    expected_values=("Town_Deal", "Future_High_Street_Fund"),
                )
            ],
        ),
        (
            {"fund": "Town_Deal", "place": "Bedford"},
            [
                UnauthorisedSubmissionFailure(
                    value_descriptor="Place Names",
                    entered_value="Bedford",
                    expected_values=("Newark",),
                )
            ],
        ),
    ],
    indirect=["mocked_project_admin_sheet"],
)
def test_full_pre_transformation_validation_pipeline_failures(mocked_project_admin_sheet, expected):
    with pytest.raises(ValidationError) as ve:
        pre_transformation_validations(
            mocked_project_admin_sheet,
            4,
            {"Place Names": ("Newark",), "Fund Types": ("Town_Deal", "Future_High_Street_Fund")},
        )

    assert ve.value.validation_failures == expected


def test_authorisation_validation_place_name(valid_workbook_round_four):
    with pytest.raises(ValidationError) as ve:
        authorisation_validation(
            valid_workbook_round_four,
            {"Place Names": ("Heanor",), "Fund Types": ("Town_Deal", "Future_High_Street_Fund")},
            TF_ROUND_4,
        )

    assert ve.value.validation_failures == [
        UnauthorisedSubmissionFailure(
            value_descriptor="Place Names", entered_value="Newark", expected_values=("Heanor",)
        )
    ]


def test_authorisation_validation_fund_type(valid_workbook_round_four):
    with pytest.raises(ValidationError) as ve:
        valid_workbook_round_four["2 - Project Admin"][4][6] = "Rotherham"  # Rotherham is both HS/TD
        authorisation_validation(
            valid_workbook_round_four,
            {"Place Names": ("Rotherham",), "Fund Types": ("Future_High_Street_Fund",)},
            TF_ROUND_4,
        )

    assert ve.value.validation_failures == [
        UnauthorisedSubmissionFailure(
            value_descriptor="Fund Types", entered_value="Town_Deal", expected_values=("Future_High_Street_Fund",)
        )
    ]


def test_wrong_input_validation_reporting_period(valid_workbook_round_four):
    with pytest.raises(ValidationError) as ve:
        valid_workbook_round_four["1 - Start Here"][1][4] = "wrong round"
        wrong_input_validation(valid_workbook_round_four, TF_ROUND_4)

    assert ve.value.validation_failures == [
        WrongInputFailure(
            value_descriptor="Reporting Period",
            entered_value="wrong round",
            expected_values=("1 April 2023 to 30 September 2023",),
        )
    ]


def test_wrong_input_validation_form_version(valid_workbook_round_four):
    with pytest.raises(ValidationError) as ve:
        valid_workbook_round_four["1 - Start Here"][1][6] = "wrong version"
        wrong_input_validation(valid_workbook_round_four, TF_ROUND_4)

    assert ve.value.validation_failures == [
        WrongInputFailure(
            value_descriptor="Form Version",
            entered_value="wrong version",
            expected_values=("Town Deals and Future High Streets " "Fund Reporting Template (v4.3)",),
        )
    ]


def test_wrong_input_validation_place_name(valid_workbook_round_four):
    with pytest.raises(ValidationError) as ve:
        valid_workbook_round_four["2 - Project Admin"][4][6] = ""
        wrong_input_validation(valid_workbook_round_four, TF_ROUND_4)

    assert ve.value.validation_failures == [
        WrongInputFailure(
            value_descriptor="Place Name",
            entered_value="",
            expected_values=tuple(TF_PLACE_NAMES_TO_ORGANISATIONS.keys()),
        )
    ]


def test_wrong_input_validation_fund_type(valid_workbook_round_four):
    with pytest.raises(ValidationError) as ve:
        valid_workbook_round_four["2 - Project Admin"][4][5] = ""
        wrong_input_validation(valid_workbook_round_four, TF_ROUND_4)

    assert ve.value.validation_failures == [
        WrongInputFailure(
            value_descriptor="Fund Type", entered_value="", expected_values=("Town_Deal", "Future_High_Street_Fund")
        )
    ]


def test_conflicting_input_validation_failure(valid_workbook_round_four):
    with pytest.raises(ValidationError) as ve:
        valid_workbook_round_four["2 - Project Admin"][4][5] = "Future_High_Street_Fund"
        conflicting_input_validation(valid_workbook_round_four, TF_ROUND_4)

    assert ve.value.validation_failures == [
        WrongInputFailure(
            value_descriptor="Place Name vs Fund Type",
            entered_value="Future_High_Street_Fund",
            expected_values=("Town_Deal",),
        )
    ]
