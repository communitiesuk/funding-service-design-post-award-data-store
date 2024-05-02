import pandas as pd

import core.transformation.pathfinders.round_1.control_mappings as pf


def test_create_control_mappings(mock_df_dict: dict[str, pd.DataFrame]):
    mappings = pf.create_control_mappings(mock_df_dict)
    expected_mappings = {
        "programme_name_to_id": {"Bolton Council": "PF-BOL"},
        "project_name_to_id": {
            "PF-BOL-001: Wellsprings Innovation Hub": "PF-BOL-001",
            "PF-BOL-002: Bolton Market Upgrades": "PF-BOL-002",
        },
    }
    assert mappings == expected_mappings


def test__programme_name_to_id(mock_df_dict: dict[str, pd.DataFrame]):
    programme_name_to_id = pf._programme_name_to_id(mock_df_dict["Project details control"])
    assert programme_name_to_id == {"Bolton Council": "PF-BOL"}


def test__project_name_to_id(mock_df_dict: dict[str, pd.DataFrame]):
    project_name_to_id = pf._project_name_to_id(mock_df_dict["Project details control"])
    assert project_name_to_id == {
        "PF-BOL-001: Wellsprings Innovation Hub": "PF-BOL-001",
        "PF-BOL-002: Bolton Market Upgrades": "PF-BOL-002",
    }
