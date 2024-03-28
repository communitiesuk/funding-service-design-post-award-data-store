from unittest.mock import patch

import pandas as pd
import pytest

from core.exceptions import ValidationError
from core.messaging import Message
from core.validation.specific_validation.pathfinders.round_1 import (
    _check_actual_forecast_reporting_period,
    _check_bespoke_outputs,
    _check_credible_plan_fields,
    _check_intervention_themes_in_pfcs,
    _check_projects,
    _check_standard_outcomes,
    cross_table_validation,
)


@pytest.fixture
def mock_control_mappings():
    return {
        "programme_name_to_id": {"Bolton Council": "PF-BOL"},
        "project_name_to_id": {
            "PF-BOL-001: Wellsprings Innovation Hub": "PF-BOL-001",
            "PF-BOL-002: Bolton Market Upgrades": "PF-BOL-002",
        },
        "programme_id_to_project_ids": {"PF-BOL": ["PF-BOL-001", "PF-BOL-002"]},
        "programme_id_to_allowed_bespoke_outputs": {"PF-BOL": ["Potential entrepreneurs assisted"]},
        "programme_id_to_allowed_bespoke_outcomes": {"PF-BOL": []},
        "intervention_theme_to_standard_outputs": {
            "Improving the quality of life of residents": ["Amount of existing parks/greenspace/outdoor improved"],
            "Enhancing subregional and regional connectivity": ["Total length of new pedestrian paths"],
        },
        "intervention_theme_to_standard_outcomes": {
            "Strengthening the visitor and local service economy": ["Audience numbers for cultural events"],
            "Unlocking and enabling industrial, commercial, and residential development": ["Vehicle flow"],
        },
        "intervention_themes": [
            "Enhancing subregional and regional connectivity",
            "Strengthening the visitor and local service economy",
            "Improving the quality of life of residents",
            "Unlocking and enabling industrial, commercial, and residential development",
        ],
    }


def test_cross_table_validation_passes(mock_df_dict, mock_control_mappings):
    with patch(
        "core.validation.specific_validation.pathfinders.round_1.create_control_mappings"
    ) as mock_create_control_mappings:
        mock_create_control_mappings.return_value = mock_control_mappings
        cross_table_validation(mock_df_dict)


def test_cross_table_validation_fails(mock_df_dict, mock_control_mappings):
    original_project_name = mock_df_dict["Project progress"]["Project name"][0]
    original_outcome = mock_df_dict["Outcomes"]["Outcome"][0]
    original_output = mock_df_dict["Bespoke outputs"]["Output"][0]
    original_underspend = mock_df_dict["Total underspend"]["Total underspend"][0]
    mock_df_dict["Project progress"]["Project name"][0] = "Invalid Project"
    mock_df_dict["Outcomes"]["Outcome"][0] = "Invalid Outcome"
    mock_df_dict["Bespoke outputs"]["Output"][0] = "Invalid Bespoke Output"
    mock_df_dict["Total underspend"]["Total underspend"][0] = pd.NA
    with pytest.raises(ValidationError) as exc_info:
        with patch(
            "core.validation.specific_validation.pathfinders.round_1.create_control_mappings"
        ) as mock_create_control_mappings:
            mock_create_control_mappings.return_value = mock_control_mappings
            cross_table_validation(mock_df_dict)
    mock_df_dict["Project progress"]["Project name"][0] = original_project_name
    mock_df_dict["Outcomes"]["Outcome"][0] = original_outcome
    mock_df_dict["Bespoke outputs"]["Output"][0] = original_output
    mock_df_dict["Total underspend"]["Total underspend"][0] = original_underspend
    assert exc_info.value.error_messages == [
        Message(
            sheet="Progress",
            section="Project progress",
            cell_index=None,
            description="Project name 'Invalid Project' is not allowed for this organisation.",
            error_type=None,
        ),
        Message(
            sheet="Outcomes",
            section="Outcomes",
            cell_index=None,
            description="Standard outcome 'Invalid Outcome' is not allowed for this intervention theme.",
            error_type=None,
        ),
        Message(
            sheet="Outputs",
            section="Bespoke outputs",
            cell_index=None,
            description="Bespoke output 'Invalid Bespoke Output' is not allowed for this organisation.",
            error_type=None,
        ),
        Message(
            sheet="Finances",
            section="Total underspend",
            cell_index=None,
            description="If you have selected 'Yes' for 'Credible Plan', you must answer Q2, Q3 and Q4.",
            error_type=None,
        ),
    ]


def test__check_projects_passes(mock_df_dict, mock_control_mappings):
    _check_projects(mock_df_dict, mock_control_mappings)


def test__check_projects_fails(mock_df_dict, mock_control_mappings):
    original_project_name = mock_df_dict["Project progress"]["Project name"][0]
    mock_df_dict["Project progress"]["Project name"][0] = "Invalid Project"
    error_messages = _check_projects(mock_df_dict, mock_control_mappings)
    mock_df_dict["Project progress"]["Project name"][0] = original_project_name
    assert error_messages == [
        Message(
            sheet="Progress",
            section="Project progress",
            cell_index=None,
            description="Project name 'Invalid Project' is not allowed for this organisation.",
            error_type=None,
        )
    ]


def test__check_standard_outcomes_passes(mock_df_dict, mock_control_mappings):
    _check_standard_outcomes(mock_df_dict, mock_control_mappings)


def test__check_standard_outcomes_fails(mock_df_dict, mock_control_mappings):
    original_outcome = mock_df_dict["Outcomes"]["Outcome"][0]
    mock_df_dict["Outcomes"]["Outcome"][0] = "Invalid Outcome"
    error_messages = _check_standard_outcomes(mock_df_dict, mock_control_mappings)
    mock_df_dict["Outcomes"]["Outcome"][0] = original_outcome
    assert error_messages == [
        Message(
            sheet="Outcomes",
            section="Outcomes",
            cell_index=None,
            description="Standard outcome 'Invalid Outcome' is not allowed for this intervention theme.",
            error_type=None,
        )
    ]


def test__check_bespoke_outputs_passes(mock_df_dict, mock_control_mappings):
    _check_bespoke_outputs(mock_df_dict, mock_control_mappings)


def test__check_bespoke_outputs_fails(mock_df_dict, mock_control_mappings):
    original_output = mock_df_dict["Bespoke outputs"]["Output"][0]
    mock_df_dict["Bespoke outputs"]["Output"][0] = "Invalid Bespoke Output"
    error_messages = _check_bespoke_outputs(mock_df_dict, mock_control_mappings)
    mock_df_dict["Bespoke outputs"]["Output"][0] = original_output
    assert error_messages == [
        Message(
            sheet="Outputs",
            section="Bespoke outputs",
            cell_index=None,
            description="Bespoke output 'Invalid Bespoke Output' is not allowed for this organisation.",
            error_type=None,
        )
    ]


def test__check_credible_plan_fields_passes(mock_df_dict):
    _check_credible_plan_fields(mock_df_dict)


def test__check_credible_plan_fields_fails(mock_df_dict):
    original_underspend = mock_df_dict["Total underspend"]["Total underspend"][0]
    mock_df_dict["Total underspend"]["Total underspend"][0] = pd.NA
    error_messages = _check_credible_plan_fields(mock_df_dict)
    mock_df_dict["Total underspend"]["Total underspend"][0] = original_underspend
    assert error_messages == [
        Message(
            sheet="Finances",
            section="Total underspend",
            cell_index=None,
            description="If you have selected 'Yes' for 'Credible Plan', you must answer Q2, Q3 and Q4.",
            error_type=None,
        )
    ]


def test__check_intervention_themes_in_pfcs_passes(mock_df_dict, mock_control_mappings):
    _check_intervention_themes_in_pfcs(mock_df_dict, mock_control_mappings)


def test__check_intervention_themes_in_pfcs_fails(mock_df_dict, mock_control_mappings):
    mock_control_mappings["intervention_themes"] = [
        "Strengthening the visitor and local service economy",
        "Unlocking and enabling industrial, commercial, and residential development",
    ]
    original_moved_from = mock_df_dict["Project finance changes"]["Intervention theme moved from"][0]
    original_moved_to = mock_df_dict["Project finance changes"]["Intervention theme moved to"][0]
    mock_df_dict["Project finance changes"]["Intervention theme moved from"][0] = "Invalid Intervention Theme"
    mock_df_dict["Project finance changes"]["Intervention theme moved to"][0] = "Another Invalid Intervention Theme"
    error_messages = _check_intervention_themes_in_pfcs(mock_df_dict, mock_control_mappings)
    mock_df_dict["Project finance changes"]["Intervention theme moved from"][0] = original_moved_from
    mock_df_dict["Project finance changes"]["Intervention theme moved to"][0] = original_moved_to
    assert error_messages == [
        Message(
            sheet="Finances",
            section="Project finance changes",
            cell_index=None,
            description="Intervention theme 'Invalid Intervention Theme' is not allowed.",
            error_type=None,
        ),
        Message(
            sheet="Finances",
            section="Project finance changes",
            cell_index=None,
            description="Intervention theme 'Another Invalid Intervention Theme' is not allowed.",
            error_type=None,
        ),
    ]


def test_check_actual_forecast_reporting_period(mock_df_dict):
    # Test case where there are no errors
    error_messages = _check_actual_forecast_reporting_period(mock_df_dict)
    assert error_messages == []

    # Test case where there is an error for an "Actual" change in a future reporting period
    original_reporting_period = mock_df_dict["Project finance changes"]["Reporting period change takes place"][0]
    mock_df_dict["Project finance changes"]["Reporting period change takes place"][
        0
    ] = "Q1 2024/25: Apr 2024 - Jun 2024"
    error_messages = _check_actual_forecast_reporting_period(mock_df_dict)
    mock_df_dict["Project finance changes"]["Reporting period change takes place"][0] = original_reporting_period
    assert error_messages == [
        Message(
            sheet="Finances",
            section="Project finance changes",
            cell_index=None,
            description="Reporting period must not be in future if 'Actual, forecast or cancelled' is 'Actual'.",
            error_type=None,
        )
    ]

    # Test case where there is an error for a "Forecast" change in a past reporting period
    original_actual_forecast = mock_df_dict["Project finance changes"]["Actual, forecast or cancelled"][0]
    mock_df_dict["Project finance changes"]["Actual, forecast or cancelled"][0] = "Forecast"
    error_messages = _check_actual_forecast_reporting_period(mock_df_dict)
    mock_df_dict["Project finance changes"]["Actual, forecast or cancelled"][0] = original_actual_forecast
    assert error_messages == [
        Message(
            sheet="Finances",
            section="Project finance changes",
            cell_index=None,
            description="Reporting period must be in future if 'Actual, forecast or cancelled' is 'Forecast'.",
            error_type=None,
        ),
    ]
