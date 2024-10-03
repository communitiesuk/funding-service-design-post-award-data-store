import pandas as pd
import pytest

from data_store.messaging import Message
from data_store.validation.pathfinders.cross_table_validation.ct_validate_r2 import (
    _check_actual_forecast_reporting_period,
    _check_current_underspend,
    _check_intervention_themes_in_pfcs,
    _check_projects,
    cross_table_validate,
)


def test_cross_table_validation_passes(mock_pf_r2_df_dict):
    error_messages = cross_table_validate(mock_pf_r2_df_dict)
    assert error_messages == []


def test_cross_table_validation_fails(mock_pf_r2_df_dict):
    # First error: Invalid project name in "Project progress"
    mock_pf_r2_df_dict["Project progress"].loc[0, "Project name"] = "Invalid Project"

    # Second error: Invalid project name in "Project location"
    mock_pf_r2_df_dict["Project location"].loc[0, "Project name"] = "Another Invalid Project"

    # Third error: Missing current underspend when reporting period is not Q4
    mock_pf_r2_df_dict["Reporting period"].iloc[0, 0] = "Q1 2024/25: Apr 2024 - Jun 2024"
    mock_pf_r2_df_dict["Current underspend"].iloc[0, 0] = pd.NA

    # Fourth error: Invalid intervention theme in "Project finance changes"
    mock_pf_r2_df_dict["Project finance changes"].loc[0, "Intervention theme moved from"] = "Invalid Theme"

    # Fifth error: Actual reporting period in the future
    mock_pf_r2_df_dict["Project finance changes"].loc[0, "Actual, forecast or cancelled"] = "Actual"
    mock_pf_r2_df_dict["Project finance changes"].loc[0, "Reporting period change takes place"] = (
        "Q2 2024/25: Jul 2024 - Sep 2024"
    )

    error_messages = cross_table_validate(mock_pf_r2_df_dict)
    expected_error_messages = [
        Message(
            sheet="Progress",
            section="Project progress",
            cell_indexes=("B1",),
            description="Project name 'Invalid Project' is not allowed for this organisation.",
            error_type=None,
        ),
        Message(
            sheet="Project location",
            section="Project location",
            cell_indexes=("B1",),
            description="Project name 'Another Invalid Project' is not allowed for this organisation.",
            error_type=None,
        ),
        Message(
            sheet="Finances",
            section="Current underspend",
            cell_indexes=("B1",),
            description="Current underspend must be filled in if the reporting period is not Q4.",
            error_type=None,
        ),
        Message(
            sheet="Finances",
            section="Project finance changes",
            cell_indexes=("E1",),
            description="Intervention theme 'Invalid Theme' is not allowed.",
            error_type=None,
        ),
        Message(
            sheet="Finances",
            section="Project finance changes",
            cell_indexes=("P1",),
            description="Reporting period must not be in the future if 'Actual, forecast or cancelled' is 'Actual'.",
            error_type=None,
        ),
    ]
    assert error_messages == expected_error_messages


def test__check_projects_passes(mock_pf_r2_df_dict):
    _check_projects(mock_pf_r2_df_dict)


def test__check_projects_fails(mock_pf_r2_df_dict):
    mock_pf_r2_df_dict["Project progress"]["Project name"][0] = "Invalid Project"
    error_messages = _check_projects(mock_pf_r2_df_dict)
    assert error_messages == [
        Message(
            sheet="Progress",
            section="Project progress",
            cell_indexes=("B1",),
            description="Project name 'Invalid Project' is not allowed for this organisation.",
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
def test__check_current_underspend_passes(mock_pf_r2_df_dict, reporting_period, current_underspend):
    mock_pf_r2_df_dict["Reporting period"].iloc[0, 0] = reporting_period
    mock_pf_r2_df_dict["Current underspend"].iloc[0, 0] = current_underspend
    error_messages = _check_current_underspend(mock_pf_r2_df_dict)
    assert error_messages == []


def test__check_current_underspend_fails(mock_pf_r2_df_dict):
    # Test case with non-Q4 reporting period and missing current underspend
    mock_pf_r2_df_dict["Reporting period"].iloc[0, 0] = "Q1 2024/25: Apr 2024 - Jun 2024"
    mock_pf_r2_df_dict["Current underspend"].iloc[0, 0] = pd.NA
    error_messages = _check_current_underspend(mock_pf_r2_df_dict)
    assert error_messages == [
        Message(
            sheet="Finances",
            section="Current underspend",
            cell_indexes=("B1",),
            description="Current underspend must be filled in if the reporting period is not Q4.",
            error_type=None,
        )
    ]


def test__check_intervention_themes_in_pfcs_passes(mock_pf_r2_df_dict):
    _check_intervention_themes_in_pfcs(mock_pf_r2_df_dict)


def test__check_intervention_themes_in_pfcs_fails(mock_pf_r2_df_dict):
    mock_pf_r2_df_dict["Project finance changes"].loc[0, "Intervention theme moved from"] = "Invalid Intervention Theme"
    mock_pf_r2_df_dict["Project finance changes"].loc[0, "Intervention theme moved to"] = (
        "Another Invalid Intervention Theme"
    )
    error_messages = _check_intervention_themes_in_pfcs(mock_pf_r2_df_dict)
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
    mock_pf_r2_df_dict, reporting_period_change_takes_place, actual_forecast
):
    assert mock_pf_r2_df_dict["Reporting period"].iloc[0, 0] == "Q4 2023/24: Jan 2024 - Mar 2024"
    mock_pf_r2_df_dict["Project finance changes"].loc[0, "Reporting period change takes place"] = (
        reporting_period_change_takes_place
    )
    mock_pf_r2_df_dict["Project finance changes"].loc[0, "Actual, forecast or cancelled"] = actual_forecast
    error_messages = _check_actual_forecast_reporting_period(mock_pf_r2_df_dict)
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
    mock_pf_r2_df_dict, reporting_period_change_takes_place, actual_forecast, expected_error_message
):
    assert mock_pf_r2_df_dict["Reporting period"].iloc[0, 0] == "Q4 2023/24: Jan 2024 - Mar 2024"
    mock_pf_r2_df_dict["Project finance changes"].loc[0, "Reporting period change takes place"] = (
        reporting_period_change_takes_place
    )
    mock_pf_r2_df_dict["Project finance changes"].loc[0, "Actual, forecast or cancelled"] = actual_forecast
    error_messages = _check_actual_forecast_reporting_period(mock_pf_r2_df_dict)
    assert error_messages == [
        Message(
            sheet="Finances",
            section="Project finance changes",
            cell_indexes=("P1",),
            description=expected_error_message,
            error_type=None,
        )
    ]
