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
        "programme_id_to_allowed_bespoke_outputs": {
            "PF-BOL": ["Amount of new office space (m2)", "Potential entrepreneurs assisted"]
        },
        "programme_id_to_allowed_bespoke_outcomes": {"PF-BOL": ["Travel times in corridors of interest"]},
        "intervention_theme_to_standard_outputs": {
            "Improving the quality of life of residents": ["Amount of existing parks/greenspace/outdoor improved"],
            "Enhancing subregional and regional connectivity": ["Total length of pedestrian paths improved"],
        },
        "intervention_theme_to_standard_outcomes": {
            "Strengthening the visitor and local service economy": ["Audience numbers for cultural events"],
            "Enhancing subregional and regional connectivity": ["Vehicle flow"],
        },
        "intervention_themes": [
            "Enhancing subregional and regional connectivity",
            "Strengthening the visitor and local service economy",
            "Improving the quality of life of residents",
            "Unlocking and enabling industrial, commercial, and residential development",  # Not needed?
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
    assert programme_id_to_allowed_bespoke_outputs == {
        "PF-BOL": ["Amount of new office space (m2)", "Potential entrepreneurs assisted"]
    }


def test__programme_id_to_allowed_bespoke_outcomes(mock_df_dict: dict[str, pd.DataFrame]):
    programme_id_to_allowed_bespoke_outcomes = pf._programme_id_to_allowed_bespoke_outcomes(
        mock_df_dict["Bespoke outcomes control"],
        pf._programme_name_to_id(mock_df_dict["Project details control"]),
    )
    assert programme_id_to_allowed_bespoke_outcomes == {"PF-BOL": ["Travel times in corridors of interest"]}
