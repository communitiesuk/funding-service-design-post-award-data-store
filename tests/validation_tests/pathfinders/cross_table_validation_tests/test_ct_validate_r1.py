import pandas as pd
import pytest

from core.messaging import Message
from core.validation.pathfinders.cross_table_validation.ct_validate_r1 import (
    _check_actual_forecast_reporting_period,
    _check_bespoke_outputs,
    _check_credible_plan_fields,
    _check_current_underspend,
    _check_intervention_themes_in_pfcs,
    _check_projects,
    _check_standard_outcomes,
    cross_table_validation,
)


def test_cross_table_validation_passes(mock_df_dict):
    error_messages = cross_table_validation(mock_df_dict)
    assert error_messages == []


def test_cross_table_validation_fails(mock_df_dict):
    mock_df_dict["Project progress"]["Project name"][0] = "Invalid Project"
    mock_df_dict["Outcomes"]["Outcome"][0] = "Invalid Outcome"
    mock_df_dict["Outcomes"]["Unit of measurement"][0] = "Invalid Unit of Measurement"
    mock_df_dict["Bespoke outputs"]["Output"][0] = "Invalid Bespoke Output"
    mock_df_dict["Total underspend"]["Total underspend"][0] = pd.NA
    mock_df_dict["Outputs"]["Unit of measurement"][0] = "Invalid Unit of Measurement"
    error_messages = cross_table_validation(mock_df_dict)
    assert error_messages == [
        Message(
            sheet="Progress",
            section="Project progress",
            cell_indexes=("B1",),
            description="Project name 'Invalid Project' is not allowed for this organisation.",
            error_type=None,
        ),
        Message(
            sheet="Outputs",
            section="Standard outputs",
            cell_indexes=("D1",),
            description="Unit of measurement 'Invalid Unit of Measurement' is not allowed for this output or outcome.",
            error_type=None,
        ),
        Message(
            sheet="Outcomes",
            section="Outcomes",
            cell_indexes=("C1",),
            description="Standard outcome value 'Invalid Outcome' is not allowed for intervention theme"
            " 'Enhancing subregional and regional connectivity'.",
            error_type=None,
        ),
        Message(
            sheet="Outputs",
            section="Bespoke outputs",
            cell_indexes=("C1",),
            description="Bespoke output value 'Invalid Bespoke Output' is not allowed for this organisation.",
            error_type=None,
        ),
        Message(
            sheet="Finances",
            section="Total underspend",
            cell_indexes=("B1",),
            description="If you have selected 'Yes' for 'Credible Plan', you must answer Q2, Q3 and Q4.",
            error_type=None,
        ),
    ]


def test__check_projects_passes(mock_df_dict):
    _check_projects(mock_df_dict)


def test__check_projects_fails(mock_df_dict):
    mock_df_dict["Project progress"]["Project name"][0] = "Invalid Project"
    error_messages = _check_projects(mock_df_dict)
    assert error_messages == [
        Message(
            sheet="Progress",
            section="Project progress",
            cell_indexes=("B1",),
            description="Project name 'Invalid Project' is not allowed for this organisation.",
            error_type=None,
        )
    ]


def test__check_standard_outcomes_passes(mock_df_dict):
    _check_standard_outcomes(mock_df_dict)


def test__check_standard_outcomes_fails(mock_df_dict):
    mock_df_dict["Outcomes"]["Outcome"][0] = "Invalid Outcome"
    error_messages = _check_standard_outcomes(mock_df_dict)
    assert error_messages == [
        Message(
            sheet="Outcomes",
            section="Outcomes",
            cell_indexes=("C1",),
            description="Standard outcome value 'Invalid Outcome' is not allowed for intervention theme"
            " 'Enhancing subregional and regional connectivity'.",
            error_type=None,
        )
    ]


def test__check_bespoke_outputs_passes(mock_df_dict):
    _check_bespoke_outputs(mock_df_dict)


def test__check_bespoke_outputs_fails(mock_df_dict):
    mock_df_dict["Bespoke outputs"]["Output"][0] = "Invalid Bespoke Output"
    error_messages = _check_bespoke_outputs(mock_df_dict)
    assert error_messages == [
        Message(
            sheet="Outputs",
            section="Bespoke outputs",
            cell_indexes=("C1",),
            description="Bespoke output value 'Invalid Bespoke Output' is not allowed for this organisation.",
            error_type=None,
        )
    ]


def test__check_credible_plan_fields_passes(mock_df_dict):
    _check_credible_plan_fields(mock_df_dict)


def test__check_credible_plan_fields_fails(mock_df_dict):
    mock_df_dict["Total underspend"]["Total underspend"][0] = pd.NA
    error_messages = _check_credible_plan_fields(mock_df_dict)
    assert error_messages == [
        Message(
            sheet="Finances",
            section="Total underspend",
            cell_indexes=("B1",),
            description="If you have selected 'Yes' for 'Credible Plan', you must answer Q2, Q3 and Q4.",
            error_type=None,
        )
    ]


@pytest.mark.parametrize(
    "reporting_period, current_underspend",
    [
        ("Q4 2023/24: Jan 2024 - Mar 2024", 0),  # Q4 reporting period with current underspend present
        ("Q4 2023/24: Jan 2024 - Mar 2024", pd.NA),  # Q4 reporting period with current underspend missing
        ("Q1 2024/25: Apr 2024 - Jun 2024", 0),  # Non-Q4 reporting period with current underspend present
    ],
)
def test__check_current_underspend_passes(mock_df_dict, reporting_period, current_underspend):
    mock_df_dict["Reporting period"].iloc[0, 0] = reporting_period
    mock_df_dict["Current underspend"].iloc[0, 0] = current_underspend
    error_messages = _check_current_underspend(mock_df_dict)
    assert error_messages == []


def test__check_current_underspend_fails(mock_df_dict):
    # Test case with non-Q4 reporting period and missing current underspend
    mock_df_dict["Reporting period"].iloc[0, 0] = "Q1 2024/25: Apr 2024 - Jun 2024"
    mock_df_dict["Current underspend"].iloc[0, 0] = pd.NA
    error_messages = _check_current_underspend(mock_df_dict)
    assert error_messages == [
        Message(
            sheet="Finances",
            section="Current underspend",
            cell_indexes=("B1",),
            description="Current underspend must be filled in if the reporting period is not Q4.",
            error_type=None,
        )
    ]


def test__check_intervention_themes_in_pfcs_passes(mock_df_dict):
    _check_intervention_themes_in_pfcs(mock_df_dict)


def test__check_intervention_themes_in_pfcs_fails(mock_df_dict):
    mock_df_dict["Project finance changes"]["Intervention theme moved from"][0] = "Invalid Intervention Theme"
    mock_df_dict["Project finance changes"]["Intervention theme moved to"][0] = "Another Invalid Intervention Theme"
    error_messages = _check_intervention_themes_in_pfcs(mock_df_dict)
    assert error_messages == [
        Message(
            sheet="Finances",
            section="Project finance changes",
            cell_indexes=("E1",),
            description="Intervention theme 'Invalid Intervention Theme' is not allowed.",
            error_type=None,
        ),
        Message(
            sheet="Finances",
            section="Project finance changes",
            cell_indexes=("I1",),
            description="Intervention theme 'Another Invalid Intervention Theme' is not allowed.",
            error_type=None,
        ),
    ]


@pytest.mark.parametrize(
    "reporting_period_change_takes_place, actual_forecast",
    [
        ("Q4 2023/24: Jan 2024 - Mar 2024", "Actual"),  # Actual change in a past reporting period
        ("Q1 2024/25: Apr 2024 - Jun 2024", "Forecast"),  # Forecast change in a future reporting period
    ],
)
def test__check_actual_forecast_reporting_period_passes(
    mock_df_dict, reporting_period_change_takes_place, actual_forecast
):
    assert mock_df_dict["Reporting period"].iloc[0, 0] == "Q4 2023/24: Jan 2024 - Mar 2024"
    mock_df_dict["Project finance changes"]["Reporting period change takes place"][0] = (
        reporting_period_change_takes_place
    )
    mock_df_dict["Project finance changes"]["Actual, forecast or cancelled"][0] = actual_forecast
    error_messages = _check_actual_forecast_reporting_period(mock_df_dict)
    assert error_messages == []


@pytest.mark.parametrize(
    "reporting_period_change_takes_place, actual_forecast, expected_error_message",
    [
        (  # Actual change in a future reporting period
            "Q1 2024/25: Apr 2024 - Jun 2024",
            "Actual",
            "Reporting period must not be in the future if 'Actual, forecast or cancelled' is 'Actual'.",
        ),
        (  # Forecast change in a past reporting period
            "Q4 2023/24: Jan 2024 - Mar 2024",
            "Forecast",
            "Reporting period must be in the future if 'Actual, forecast or cancelled' is 'Forecast'.",
        ),
    ],
)
def test__check_actual_forecast_reporting_period_fails(
    mock_df_dict, reporting_period_change_takes_place, actual_forecast, expected_error_message
):
    assert mock_df_dict["Reporting period"].iloc[0, 0] == "Q4 2023/24: Jan 2024 - Mar 2024"
    mock_df_dict["Project finance changes"]["Reporting period change takes place"][0] = (
        reporting_period_change_takes_place
    )
    mock_df_dict["Project finance changes"]["Actual, forecast or cancelled"][0] = actual_forecast
    error_messages = _check_actual_forecast_reporting_period(mock_df_dict)
    assert error_messages == [
        Message(
            sheet="Finances",
            section="Project finance changes",
            cell_indexes=("P1",),
            description=expected_error_message,
            error_type=None,
        )
    ]
