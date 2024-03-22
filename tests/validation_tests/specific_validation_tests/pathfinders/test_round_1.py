from unittest.mock import patch

import pandas as pd
import pytest

from core.exceptions import ValidationError
from core.messaging import Message
from core.validation.specific_validation.pathfinders.round_1 import (
    _check_bespoke_outputs_outcomes,
    _check_credible_plan_fields,
    _check_projects,
    _check_standard_outputs_outcomes,
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
        "standard_outputs": ["Total length of new pedestrian paths"],
        "standard_outcomes": ["Vehicle flow"],
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
            description="Project name Invalid Project is not allowed for this organisation.",
            error_type=None,
        ),
        Message(
            sheet="Outcomes",
            section="Outcomes",
            cell_index=None,
            description="Standard output or outcome value Invalid Outcome not in allowed values.",
            error_type=None,
        ),
        Message(
            sheet="Outputs",
            section="Bespoke outputs",
            cell_index=None,
            description="Bespoke output or outcome value Invalid Bespoke Output is not allowed for this organisation.",
            error_type=None,
        ),
        Message(
            sheet="Finances",
            section="Total underspend",
            cell_index=None,
            description="If credible plan is selected, you must answer Q2, Q3 and Q4.",
            error_type=None,
        ),
    ]


def test_check_projects_passes(mock_df_dict, mock_control_mappings):
    _check_projects(mock_df_dict, mock_control_mappings)


def test_check_projects_fails(mock_df_dict, mock_control_mappings):
    original_project_name = mock_df_dict["Project progress"]["Project name"][0]
    mock_df_dict["Project progress"]["Project name"][0] = "Invalid Project"
    with patch(
        "core.validation.specific_validation.pathfinders.round_1.create_control_mappings"
    ) as mock_create_control_mappings:
        mock_create_control_mappings.return_value = mock_control_mappings
        error_messages = _check_projects(mock_df_dict, mock_control_mappings)
    mock_df_dict["Project progress"]["Project name"][0] = original_project_name
    assert error_messages == [
        Message(
            sheet="Progress",
            section="Project progress",
            cell_index=None,
            description="Project name Invalid Project is not allowed for this organisation.",
            error_type=None,
        )
    ]


def test_check_standard_outputs_outcomes_passes(mock_df_dict, mock_control_mappings):
    _check_standard_outputs_outcomes(mock_df_dict, mock_control_mappings)


def test_check_standard_outputs_outcomes_fails(mock_df_dict, mock_control_mappings):
    original_outcome = mock_df_dict["Outcomes"]["Outcome"][0]
    mock_df_dict["Outcomes"]["Outcome"][0] = "Invalid Outcome"
    with patch(
        "core.validation.specific_validation.pathfinders.round_1.create_control_mappings"
    ) as mock_create_control_mappings:
        mock_create_control_mappings.return_value = mock_control_mappings
        error_messages = _check_standard_outputs_outcomes(mock_df_dict, mock_control_mappings)
    mock_df_dict["Outcomes"]["Outcome"][0] = original_outcome
    assert error_messages == [
        Message(
            sheet="Outcomes",
            section="Outcomes",
            cell_index=None,
            description="Standard output or outcome value Invalid Outcome not in allowed values.",
            error_type=None,
        )
    ]


def test_check_bespoke_outputs_outcomes_passes(mock_df_dict, mock_control_mappings):
    _check_bespoke_outputs_outcomes(mock_df_dict, mock_control_mappings)


def test_check_bespoke_outputs_outcomes_fails(mock_df_dict, mock_control_mappings):
    original_output = mock_df_dict["Bespoke outputs"]["Output"][0]
    mock_df_dict["Bespoke outputs"]["Output"][0] = "Invalid Bespoke Output"
    with patch(
        "core.validation.specific_validation.pathfinders.round_1.create_control_mappings"
    ) as mock_create_control_mappings:
        mock_create_control_mappings.return_value = mock_control_mappings
        error_messages = _check_bespoke_outputs_outcomes(mock_df_dict, mock_control_mappings)
    mock_df_dict["Bespoke outputs"]["Output"][0] = original_output
    assert error_messages == [
        Message(
            sheet="Outputs",
            section="Bespoke outputs",
            cell_index=None,
            description="Bespoke output or outcome value Invalid Bespoke Output is not allowed for this organisation.",
            error_type=None,
        )
    ]


def test_check_credible_plan_fields_passes(mock_df_dict, mock_control_mappings):
    _check_credible_plan_fields(mock_df_dict, mock_control_mappings)


def test_check_credible_plan_fields_fails(mock_df_dict, mock_control_mappings):
    original_underspend = mock_df_dict["Total underspend"]["Total underspend"][0]
    mock_df_dict["Total underspend"]["Total underspend"][0] = pd.NA
    with patch(
        "core.validation.specific_validation.pathfinders.round_1.create_control_mappings"
    ) as mock_create_control_mappings:
        mock_create_control_mappings.return_value = mock_control_mappings
        error_messages = _check_credible_plan_fields(mock_df_dict, mock_control_mappings)
    mock_df_dict["Total underspend"]["Total underspend"][0] = original_underspend
    assert error_messages == [
        Message(
            sheet="Finances",
            section="Total underspend",
            cell_index=None,
            description="If credible plan is selected, you must answer Q2, Q3 and Q4.",
            error_type=None,
        )
    ]
