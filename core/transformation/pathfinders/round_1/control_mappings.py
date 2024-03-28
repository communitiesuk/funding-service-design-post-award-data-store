"""
This module contains functions to create mappings from control data tables to be used for validation and transformation
downstream. These mappings are more Pythonic representations of the control data tables and reduce the need for
DataFrame lookups during cross-table validation and transformation.
"""

import pandas as pd


def create_control_mappings(extracted_tables: dict[str, pd.DataFrame]) -> dict[str, dict | list[str]]:
    """
    Creates mappings from control data tables to be used for validation and transformation downstream. Mappings created
    are:
        - Programme name        -> Programme ID
        - Project name          -> Project ID
        - Programme ID          -> List of Project IDs
        - Programme ID          -> List of allowed bespoke outputs
        - Programme ID          -> List of allowed bespoke outcomes
        - Intervention theme    -> List of standard outputs
        - Intervention theme    -> List of standard outcomes
        - List of intervention themes
    """
    project_details_df = extracted_tables["Project details control"]
    bespoke_outputs_df = extracted_tables["Bespoke outputs control"]
    bespoke_outcomes_df = extracted_tables["Bespoke outcomes control"]
    standard_outputs_df = extracted_tables["Outputs control"]
    standard_outcomes_df = extracted_tables["Outcomes control"]
    intervention_themes_df = extracted_tables["Intervention themes control"]
    return {
        "programme_name_to_id": _programme_name_to_id(project_details_df),
        "project_id_to_name": _project_id_to_name(project_details_df),
        "project_name_to_id": _project_name_to_id(project_details_df),
        "programme_id_to_project_ids": _programme_id_to_project_ids(project_details_df),
        "programme_id_to_allowed_bespoke_outputs": _programme_id_to_allowed_bespoke_outputs(
            bespoke_outputs_df, _programme_name_to_id(project_details_df)
        ),
        "programme_id_to_allowed_bespoke_outcomes": _programme_id_to_allowed_bespoke_outcomes(
            bespoke_outcomes_df, _programme_name_to_id(project_details_df)
        ),
        "intervention_theme_to_standard_outputs": _intervention_theme_to_standard_outputs(standard_outputs_df),
        "intervention_theme_to_standard_outcomes": _intervention_theme_to_standard_outcomes(standard_outcomes_df),
        "intervention_themes": intervention_themes_df["Intervention theme"].tolist(),
    }


def _programme_name_to_id(project_details_df: pd.DataFrame) -> dict[str, str]:
    """Creates a mapping from programme name to programme ID."""
    return {row["Local Authority"]: row["Reference"][:6] for _, row in project_details_df.iterrows()}


def _project_id_to_name(project_details_df: pd.DataFrame) -> dict[str, str]:
    """Creates a mapping from project ID to project name."""
    return {row["Reference"]: row["Full name"] for _, row in project_details_df.iterrows()}


def _project_name_to_id(project_details_df: pd.DataFrame) -> dict[str, str]:
    """Creates a mapping from project name to project ID."""
    return {row["Full name"]: row["Reference"] for _, row in project_details_df.iterrows()}


def _programme_id_to_project_ids(project_details_df: pd.DataFrame) -> dict[str, list[str]]:
    """Creates a mapping from programme ID to a list of project IDs for that programme."""
    return {
        programme_id: project_details_df.loc[
            project_details_df["Reference"].str.startswith(programme_id), "Reference"
        ].tolist()
        for programme_id in _programme_name_to_id(project_details_df).values()
    }


def _programme_id_to_allowed_bespoke_outputs(
    bespoke_outputs_df: pd.DataFrame, programme_name_to_id: dict[str, str]
) -> dict[str, list[str]]:
    """Creates a mapping from programme ID to a list of allowed bespoke outputs for that programme."""
    return {
        programme_id: bespoke_outputs_df.loc[bespoke_outputs_df["Local Authority"] == programme_name, "Output"].tolist()
        for programme_name, programme_id in programme_name_to_id.items()
    }


def _programme_id_to_allowed_bespoke_outcomes(
    bespoke_outcomes_df: pd.DataFrame, programme_name_to_id: dict[str, str]
) -> dict[str, list[str]]:
    """Creates a mapping from programme ID to a list of allowed bespoke outcomes for that programme."""
    return {
        programme_id: bespoke_outcomes_df.loc[
            bespoke_outcomes_df["Local Authority"] == programme_name, "Outcome"
        ].tolist()
        for programme_name, programme_id in programme_name_to_id.items()
    }


def _intervention_theme_to_standard_outputs(standard_outputs_df: pd.DataFrame) -> dict[str, list[str]]:
    """Creates a mapping from intervention theme to a list of standard outputs for that theme."""
    return {
        row["Intervention theme"]: standard_outputs_df.loc[
            standard_outputs_df["Intervention theme"] == row["Intervention theme"], "Standard output"
        ].tolist()
        for _, row in standard_outputs_df.iterrows()
        if not pd.isna(row["Intervention theme"])
    }


def _intervention_theme_to_standard_outcomes(standard_outcomes_df: pd.DataFrame) -> dict[str, list[str]]:
    """Creates a mapping from intervention theme to a list of standard outcomes for that theme."""
    return {
        row["Intervention theme"]: standard_outcomes_df.loc[
            standard_outcomes_df["Intervention theme"] == row["Intervention theme"], "Standard outcome"
        ].tolist()
        for _, row in standard_outcomes_df.iterrows()
        if not pd.isna(row["Intervention theme"])
    }
