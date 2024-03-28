import pandas as pd

import core.transformation.pathfinders.round_1.control_mappings as pf


def test_create_control_mappings(mock_df_dict: dict[str, pd.DataFrame]):
    mappings = pf.create_control_mappings(mock_df_dict)
    expected_mappings = {
        "programme_name_to_id": {"Bolton Council": "PF-BOL"},
        "project_id_to_name": {
            "PF-BOL-001": "PF-BOL-001: Wellsprings Innovation Hub",
            "PF-BOL-002": "PF-BOL-002: Bolton Market Upgrades",
        },
        "project_name_to_id": {
            "PF-BOL-001: Wellsprings Innovation Hub": "PF-BOL-001",
            "PF-BOL-002: Bolton Market Upgrades": "PF-BOL-002",
        },
        "programme_id_to_project_ids": {"PF-BOL": ["PF-BOL-001", "PF-BOL-002"]},
        "programme_id_to_allowed_bespoke_outputs": {"PF-BOL": ["Amount of new office space (m2)"]},
        "programme_id_to_allowed_bespoke_outcomes": {"PF-BOL": ["Travel times in corridors of interest"]},
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
    assert mappings == expected_mappings


def test__programme_name_to_id(mock_df_dict: dict[str, pd.DataFrame]):
    programme_name_to_id = pf._programme_name_to_id(mock_df_dict["Project details control"])
    assert programme_name_to_id == {"Bolton Council": "PF-BOL"}


def test__project_id_to_name(mock_df_dict: dict[str, pd.DataFrame]):
    project_id_to_name = pf._project_id_to_name(mock_df_dict["Project details control"])
    assert project_id_to_name == {
        "PF-BOL-001": "PF-BOL-001: Wellsprings Innovation Hub",
        "PF-BOL-002": "PF-BOL-002: Bolton Market Upgrades",
    }


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
