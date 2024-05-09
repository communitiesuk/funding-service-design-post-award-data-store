import pytest

from core.const import TF_ROUND_4_TEMPLATE_VERSION
from core.exceptions import InitialValidationError
from core.validation.initial_validation.initial_validate import initial_validate
from core.validation.initial_validation.schemas import (
    TF_ROUND_3_INIT_VAL_SCHEMA,
    TF_ROUND_4_INIT_VAL_SCHEMA,
)

STANDARD_AUTH = {"Place Names": ("Newark",), "Fund Types": ("Town_Deal", "Future_High_Street_Fund")}


@pytest.fixture
def standard_auth():
    return STANDARD_AUTH


@pytest.fixture
def mocked_start_here_sheet(valid_workbook_round_four, request):
    valid_workbook_round_four["1 - Start Here"][1] = [
        "",
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
            STANDARD_AUTH,
        ),
        (
            {
                "reporting_round": "1 April 2023 to 30 September 2023",
                "form_version": "Town Deals and Future High Streets Fund Reporting Template (v4.3)",
            },
            TF_ROUND_4_INIT_VAL_SCHEMA,
            STANDARD_AUTH,
        ),
        (
            {
                "reporting_round": "1 October 2022 to 31 March 2023",
                "form_version": "Town Deals and Future High Streets Fund Reporting Template (v3.0)",
            },
            TF_ROUND_3_INIT_VAL_SCHEMA,
            STANDARD_AUTH,
        ),
    ],
    indirect=["mocked_start_here_sheet"],
)
def test_pre_transformation_validations_pipeline_success(
    mocked_start_here_sheet,
    schema,
    auth,
):
    initial_validate(
        mocked_start_here_sheet,
        schema,
        auth,
    )


@pytest.fixture
def mocked_project_admin_sheet(valid_workbook_round_four, request):
    valid_workbook_round_four["2 - Project Admin"][4] = [
        "",
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
    "mocked_project_admin_sheet, auth, expected",
    [
        (  # Newark is only a Town_Deal and so cannot be submitted as a Future_High_Street_Fund
            {"fund": "Future_High_Street_Fund", "place": "Newark"},
            STANDARD_AUTH,
            [
                "We do not recognise the combination of fund type and place name in cells E7 and E8 in "
                "“project admin”. Check the data is correct."
            ],
        ),
        (
            {"fund": "Future_High_Street_Fund", "place": ""},
            None,
            [
                "Cell E8 in the “project admin” must contain a place name from the dropdown list provided. "
                "Do not enter your own content."
            ],
        ),
        (
            {"fund": "", "place": "Newark"},
            None,
            [
                "Cell E7 in the “project admin” must contain a fund type from the dropdown list provided. "
                "Do not enter your own content."
            ],
        ),
        (
            {"fund": "Town_Deal", "place": "Bedford"},
            STANDARD_AUTH,
            ["You’re not authorised to submit for Bedford. You can only submit for Newark."],
        ),
    ],
    indirect=["mocked_project_admin_sheet"],
)
def test_full_pre_transformation_validation_pipeline_failures(mocked_project_admin_sheet, auth, expected):
    with pytest.raises(InitialValidationError) as ve:
        initial_validate(
            mocked_project_admin_sheet,
            TF_ROUND_4_INIT_VAL_SCHEMA,
            auth,
        )

    assert ve.value.error_messages == expected


def test_initial_validation_authorised_place_name(valid_workbook_round_four):
    with pytest.raises(InitialValidationError) as ve:
        initial_validate(
            workbook=valid_workbook_round_four,
            schema=TF_ROUND_4_INIT_VAL_SCHEMA,
            auth={"Place Names": ("Heanor",), "Fund Types": ("Town_Deal", "Future_High_Street_Fund")},
        )

    assert ve.value.error_messages == ["You’re not authorised to submit for Newark. You can only submit for Heanor."]


def test_initial_validation_authorised_fund_type(valid_workbook_round_four):
    with pytest.raises(InitialValidationError) as ve:
        valid_workbook_round_four["2 - Project Admin"].iat[7, 4] = "Rotherham"  # Rotherham is both HS/TD
        initial_validate(
            workbook=valid_workbook_round_four,
            schema=TF_ROUND_4_INIT_VAL_SCHEMA,
            auth={"Place Names": ("Rotherham",), "Fund Types": ("Future_High_Street_Fund",)},
        )
    assert ve.value.error_messages == [
        "You’re not authorised to submit for Town_Deal. You can only submit for Future_High_Street_Fund."
    ]


def test_initial_validation_reporting_period(valid_workbook_round_four, standard_auth):
    with pytest.raises(InitialValidationError) as ve:
        valid_workbook_round_four["1 - Start Here"].iat[5, 1] = "wrong round"
        initial_validate(
            workbook=valid_workbook_round_four,
            schema=TF_ROUND_4_INIT_VAL_SCHEMA,
            auth=standard_auth,
        )
    assert ve.value.error_messages == [
        "Cell B6 in the “start here” tab must say “1 April 2023 to 30 September 2023”. Select this option from the "
        "dropdown list provided."
    ]


def test_initial_validation_form_version(valid_workbook_round_four, standard_auth):
    with pytest.raises(InitialValidationError) as ve:
        valid_workbook_round_four["1 - Start Here"].iat[7, 1] = "wrong version"
        initial_validate(
            workbook=valid_workbook_round_four,
            schema=TF_ROUND_4_INIT_VAL_SCHEMA,
            auth=standard_auth,
        )
    assert ve.value.error_messages == [
        f"The selected file must be the Town Deals and Future High Streets Fund Reporting Template "
        f"({TF_ROUND_4_TEMPLATE_VERSION})."
    ]


def test_initial_validation_place_name(valid_workbook_round_four):
    with pytest.raises(InitialValidationError) as ve:
        valid_workbook_round_four["2 - Project Admin"].iat[7, 4] = ""
        initial_validate(
            workbook=valid_workbook_round_four,
            schema=TF_ROUND_4_INIT_VAL_SCHEMA,
            auth=None,
        )
    assert ve.value.error_messages == [
        "Cell E8 in the “project admin” must contain a place name from the dropdown list provided. Do not enter your "
        "own content.",
    ]


def test_initial_validation_fund_type(valid_workbook_round_four):
    with pytest.raises(InitialValidationError) as ve:
        valid_workbook_round_four["2 - Project Admin"].iat[6, 4] = ""
        initial_validate(
            workbook=valid_workbook_round_four,
            schema=TF_ROUND_4_INIT_VAL_SCHEMA,
            auth=None,
        )
    assert ve.value.error_messages == [
        "Cell E7 in the “project admin” must contain a fund type from the dropdown list provided. Do not enter your "
        "own content.",
    ]


def test_initial_validation_conflicting_input(valid_workbook_round_four, standard_auth):
    with pytest.raises(InitialValidationError) as ve:
        valid_workbook_round_four["2 - Project Admin"].iat[6, 4] = "Future_High_Street_Fund"
        initial_validate(
            workbook=valid_workbook_round_four,
            schema=TF_ROUND_4_INIT_VAL_SCHEMA,
            auth=standard_auth,
        )
    assert ve.value.error_messages == [
        "We do not recognise the combination of fund type and place name in cells E7 and E8 in “project admin”. "
        "Check the data is correct.",
    ]
