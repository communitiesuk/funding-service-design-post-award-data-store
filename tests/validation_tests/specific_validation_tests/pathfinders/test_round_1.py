from unittest.mock import patch

import pandas as pd
import pytest

from core.messaging import Message
from core.validation.specific_validation.pathfinders.round_1 import (
    _check_actual_forecast_reporting_period,
    _check_bespoke_outputs,
    _check_credible_plan_fields,
    _check_current_underspend,
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
        "programme_id_to_allowed_bespoke_outputs": {
            "PF-BOL": ["Amount of new office space (m2)", "Potential entrepreneurs assisted"]
        },
        "programme_id_to_allowed_bespoke_outcomes": {"PF-BOL": ["Travel times in corridors of interest"]},
        "intervention_theme_to_standard_outputs": {
            "Improving the quality of life of residents": ["Amount of existing parks/greenspace/outdoor improved"],
            # simulating the spelling error in the spreadsheet
            "Enhancing sub-regional and regional connectivity": [
                "Amount of land made wheelchair accessible/step free ",
                "Total length of pedestrian paths improved",
            ],
        },
        "intervention_theme_to_standard_outcomes": {
            "Strengthening the visitor and local service economy": ["Audience numbers for cultural events"],
            # simulating the spelling error in the spreadsheet
            "Enhancing sub-regional and regional connectivity": ["Footfall", "Vehicle flow"],
        },
        "intervention_themes": [
            "Enhancing subregional and regional connectivity",
            "Strengthening the visitor and local service economy",
            "Improving the quality of life of residents",
            "Unlocking and enabling industrial, commercial, and residential development",
        ],
        "standard_output_uoms": {
            "Amount of existing parks/greenspace/outdoor improved": ["sqm"],
            "Total length of pedestrian paths improved": ["km"],
        },
        "standard_outcome_uoms": {"Audience numbers for cultural events": ["n of"], "Vehicle flow": ["n of"]},
        "bespoke_output_uoms": {
            "Amount of new office space (m2)": ["sqm"],
            "Potential entrepreneurs assisted": ["n of"],
        },
        "bespoke_outcome_uoms": {"Travel times in corridors of interest": ["%"]},
    }


def test_cross_table_validation_passes(mock_df_dict, mock_control_mappings):
    with patch(
        "core.validation.specific_validation.pathfinders.round_1.create_control_mappings"
    ) as mock_create_control_mappings:
        mock_create_control_mappings.return_value = mock_control_mappings
        error_messages = cross_table_validation(mock_df_dict)
    assert error_messages == []


def test_cross_table_validation_fails(mock_df_dict, mock_control_mappings):
    mock_df_dict["Project progress"]["Project name"][0] = "Invalid Project"
    mock_df_dict["Outcomes"]["Outcome"][0] = "Invalid Outcome"
    mock_df_dict["Outcomes"]["Unit of measurement"][0] = "Invalid Unit of Measurement"
    mock_df_dict["Bespoke outputs"]["Output"][0] = "Invalid Bespoke Output"
    mock_df_dict["Total underspend"]["Total underspend"][0] = pd.NA
    mock_df_dict["Outputs"]["Unit of measurement"][0] = "Invalid Unit of Measurement"
    with patch(
        "core.validation.specific_validation.pathfinders.round_1.create_control_mappings"
    ) as mock_create_control_mappings:
        mock_create_control_mappings.return_value = mock_control_mappings
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


def test__check_projects_passes(mock_df_dict, mock_control_mappings):
    _check_projects(mock_df_dict, mock_control_mappings)


def test__check_projects_fails(mock_df_dict, mock_control_mappings):
    mock_df_dict["Project progress"]["Project name"][0] = "Invalid Project"
    error_messages = _check_projects(mock_df_dict, mock_control_mappings)
    assert error_messages == [
        Message(
            sheet="Progress",
            section="Project progress",
            cell_indexes=("B1",),
            description="Project name 'Invalid Project' is not allowed for this organisation.",
            error_type=None,
        )
    ]


def test__check_standard_outcomes_passes(mock_df_dict, mock_control_mappings):
    _check_standard_outcomes(mock_df_dict, mock_control_mappings)


def test__check_standard_outcomes_fails(mock_df_dict, mock_control_mappings):
    mock_df_dict["Outcomes"]["Outcome"][0] = "Invalid Outcome"
    error_messages = _check_standard_outcomes(mock_df_dict, mock_control_mappings)
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


def test__check_bespoke_outputs_passes(mock_df_dict, mock_control_mappings):
    _check_bespoke_outputs(mock_df_dict, mock_control_mappings)


def test__check_bespoke_outputs_fails(mock_df_dict, mock_control_mappings):
    mock_df_dict["Bespoke outputs"]["Output"][0] = "Invalid Bespoke Output"
    error_messages = _check_bespoke_outputs(mock_df_dict, mock_control_mappings)
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


def test__check_intervention_themes_in_pfcs_passes(mock_df_dict, mock_control_mappings):
    _check_intervention_themes_in_pfcs(mock_df_dict, mock_control_mappings)


def test__check_intervention_themes_in_pfcs_fails(mock_df_dict, mock_control_mappings):
    mock_control_mappings["intervention_themes"] = [
        "Strengthening the visitor and local service economy",
        "Unlocking and enabling industrial, commercial, and residential development",
    ]
    mock_df_dict["Project finance changes"]["Intervention theme moved from"][0] = "Invalid Intervention Theme"
    mock_df_dict["Project finance changes"]["Intervention theme moved to"][0] = "Another Invalid Intervention Theme"
    error_messages = _check_intervention_themes_in_pfcs(mock_df_dict, mock_control_mappings)
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


def test_check_actual_forecast_reporting_period(mock_df_dict):
    # Test case where there are no errors
    error_messages = _check_actual_forecast_reporting_period(mock_df_dict)
    assert error_messages == []

    # Test case where there is an error for an "Actual" change in a future reporting period
    original_reporting_period = mock_df_dict["Project finance changes"]["Reporting period change takes place"][0]
    mock_df_dict["Project finance changes"]["Reporting period change takes place"][0] = (
        "Q1 2024/25: Apr 2024 - Jun 2024"
    )
    error_messages = _check_actual_forecast_reporting_period(mock_df_dict)
    mock_df_dict["Project finance changes"]["Reporting period change takes place"][0] = original_reporting_period
    assert error_messages == [
        Message(
            sheet="Finances",
            section="Project finance changes",
            cell_indexes=("P1",),
            description="Reporting period must not be in the future if 'Actual, forecast or cancelled' is 'Actual'.",
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
            cell_indexes=("P1",),
            description="Reporting period must be in the future if 'Actual, forecast or cancelled' is 'Forecast'.",
            error_type=None,
        ),
    ]
