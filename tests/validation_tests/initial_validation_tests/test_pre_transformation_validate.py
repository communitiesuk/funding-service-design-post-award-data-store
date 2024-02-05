import pytest

from core.const import TF_PLACE_NAMES_TO_ORGANISATIONS
from core.exceptions import ValidationError
from core.validation.failures.user import (
    UnauthorisedSubmissionFailure,
    WrongInputFailure,
)
from core.validation.initial_validation.schemas import (
    PF_INITIAL_VAL_SCHEMA,
    TF_ROUND_3_INIT_VAL_SCHEMA,
    TF_ROUND_4_INIT_VAL_SCHEMA,
)
from core.validation.initial_validation.validate import (
    authorisation_validation,
    conflicting_input_validation,
    initial_validate,
    wrong_input_validation,
)


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
    "mocked_start_here_sheet, schema, auth",
    [
        (
            {
                "reporting_round": "1 April 2023 to 30 September 2023",
                "form_version": "Town Deals and Future High Streets Fund Reporting Template (v4.3)",
            },
            TF_ROUND_4_INIT_VAL_SCHEMA,
            {"Place Names": ("Newark",), "Fund Types": ("Town_Deal",)},
        ),
        (
            {
                "reporting_round": "1 April 2023 to 30 September 2023",
                "form_version": "Town Deals and Future High Streets Fund Reporting Template (v4.3)",
            },
            TF_ROUND_4_INIT_VAL_SCHEMA,
            None,
        ),
        (
            {
                "reporting_round": "1 October 2022 to 31 March 2023",
                "form_version": "Town Deals and Future High Streets Fund Reporting Template (v3.0)",
            },
            TF_ROUND_3_INIT_VAL_SCHEMA,
            {"Place Names": ("Newark",), "Fund Types": ("Town_Deal",)},
        ),
    ],
    indirect=["mocked_start_here_sheet"],
)
def test_pre_transformation_validations_pipeline_success(
    mocked_start_here_sheet,
    schema,
    auth,
):
    errors = initial_validate(
        mocked_start_here_sheet,
        schema,
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
        initial_validate(
            mocked_project_admin_sheet,
            TF_ROUND_4_INIT_VAL_SCHEMA,
            {"Place Names": ("Newark",), "Fund Types": ("Town_Deal", "Future_High_Street_Fund")},
        )

    assert ve.value.validation_failures == expected


def test_authorisation_validation_place_name(valid_workbook_round_four):
    with pytest.raises(ValidationError) as ve:
        authorisation_validation(
            valid_workbook_round_four,
            {"Place Names": ("Heanor",), "Fund Types": ("Town_Deal", "Future_High_Street_Fund")},
            TF_ROUND_4_INIT_VAL_SCHEMA,
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
            TF_ROUND_4_INIT_VAL_SCHEMA,
        )

    assert ve.value.validation_failures == [
        UnauthorisedSubmissionFailure(
            value_descriptor="Fund Types", entered_value="Town_Deal", expected_values=("Future_High_Street_Fund",)
        )
    ]


def test_wrong_input_validation_reporting_period(valid_workbook_round_four):
    with pytest.raises(ValidationError) as ve:
        valid_workbook_round_four["1 - Start Here"][1][4] = "wrong round"
        wrong_input_validation(valid_workbook_round_four, TF_ROUND_4_INIT_VAL_SCHEMA)

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
        wrong_input_validation(valid_workbook_round_four, TF_ROUND_4_INIT_VAL_SCHEMA)

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
        wrong_input_validation(valid_workbook_round_four, TF_ROUND_4_INIT_VAL_SCHEMA)

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
        wrong_input_validation(valid_workbook_round_four, TF_ROUND_4_INIT_VAL_SCHEMA)

    assert ve.value.validation_failures == [
        WrongInputFailure(
            value_descriptor="Fund Type", entered_value="", expected_values=("Town_Deal", "Future_High_Street_Fund")
        )
    ]


def test_conflicting_input_validation_failure(valid_workbook_round_four):
    with pytest.raises(ValidationError) as ve:
        valid_workbook_round_four["2 - Project Admin"][4][5] = "Future_High_Street_Fund"
        conflicting_input_validation(valid_workbook_round_four, TF_ROUND_4_INIT_VAL_SCHEMA)

    assert ve.value.validation_failures == [
        WrongInputFailure(
            value_descriptor="Place Name vs Fund Type",
            entered_value="Future_High_Street_Fund",
            expected_values=("Town_Deal",),
        )
    ]


@pytest.fixture
def mocked_pf_start_sheet(valid_pf_workbook_round_one, request):
    valid_pf_workbook_round_one["Start"][1] = [
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
    return valid_pf_workbook_round_one


@pytest.mark.parametrize(
    "mocked_pf_start_sheet, schema, auth",
    [
        (
            {
                "reporting_round": "Q3 Oct - Dec 23/24",
                "form_version": "V 4.0",
            },
            PF_INITIAL_VAL_SCHEMA,
            {"Place Names": ("Rotherham Metropolitan Borough Council",), "Fund Types": ("Fund Name",)},
        ),
    ],
    indirect=["mocked_pf_start_sheet"],
)
def test_path_finders_initial_validation(
    mocked_pf_start_sheet,
    schema,
    auth,
):
    errors = initial_validate(
        mocked_pf_start_sheet,
        schema,
        auth,
    )
    assert errors is None
