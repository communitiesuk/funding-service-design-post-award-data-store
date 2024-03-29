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
        "programme_id_to_project_ids": {"PF-BOL": ["PF-BOL-001", "PF-BOL-002"]},
        "programme_id_to_allowed_bespoke_outputs": {"PF-BOL": ["Amount of new office space (m2)"]},
        "programme_id_to_allowed_bespoke_outcomes": {"PF-BOL": ["Travel times in corridors of interest"]},
        "standard_outcomes": ["Audience numbers for cultural events"],
        "standard_outputs": ["Amount of existing parks/greenspace/outdoor improved"],
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


def test__programme_id_to_project_ids(mock_df_dict: dict[str, pd.DataFrame]):
    programme_id_to_project_ids = pf._programme_id_to_project_ids(mock_df_dict["Project details control"])
    assert programme_id_to_project_ids == {"PF-BOL": ["PF-BOL-001", "PF-BOL-002"]}


def test__programme_id_to_allowed_bespoke_outputs(mock_df_dict: dict[str, pd.DataFrame]):
    programme_id_to_allowed_bespoke_outputs = pf._programme_id_to_allowed_bespoke_outputs(
        mock_df_dict["Bespoke outputs control"], pf._programme_name_to_id(mock_df_dict["Project details control"])
    )
    assert programme_id_to_allowed_bespoke_outputs == {"PF-BOL": ["Amount of new office space (m2)"]}


def test__programme_id_to_allowed_bespoke_outcomes(mock_df_dict: dict[str, pd.DataFrame]):
    programme_id_to_allowed_bespoke_outcomes = pf._programme_id_to_allowed_bespoke_outcomes(
        mock_df_dict["Bespoke outcomes control"],
        pf._programme_name_to_id(mock_df_dict["Project details control"]),
    )
    assert programme_id_to_allowed_bespoke_outcomes == {"PF-BOL": ["Travel times in corridors of interest"]}
