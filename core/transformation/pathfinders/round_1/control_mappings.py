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
        "project_name_to_id": _project_name_to_id(project_details_df),
        "programme_to_projects": _programme_to_projects(project_details_df),
        "programme_id_to_allowed_bespoke_outputs": _programme_id_to_allowed_bespoke_outputs(
            bespoke_outputs_df, _programme_name_to_id(project_details_df)
        ),
        "programme_id_to_allowed_bespoke_outcomes": _programme_id_to_allowed_bespoke_outcomes(
            bespoke_outcomes_df, _programme_name_to_id(project_details_df)
        ),
        "intervention_theme_to_standard_outputs": _intervention_theme_to_standard_outputs(standard_outputs_df),
        "intervention_theme_to_standard_outcomes": _intervention_theme_to_standard_outcomes(standard_outcomes_df),
        "intervention_themes": intervention_themes_df["Intervention theme"].tolist(),
        "standard_output_uoms": _output_outcome_uoms(standard_outputs_df, "Standard output"),
        "standard_outcome_uoms": _output_outcome_uoms(standard_outcomes_df, "Standard outcome"),
        "bespoke_output_uoms": _output_outcome_uoms(bespoke_outputs_df, "Output"),
        "bespoke_outcome_uoms": _output_outcome_uoms(bespoke_outcomes_df, "Outcome"),
    }


def _programme_name_to_id(project_details_df: pd.DataFrame) -> dict[str, str]:
    """Creates a mapping from programme name to programme ID."""
    return {row["Local Authority"]: row["Reference"][:6] for _, row in project_details_df.iterrows()}


def _project_name_to_id(project_details_df: pd.DataFrame) -> dict[str, str]:
    """Creates a mapping from project name to project ID."""
    return {row["Full name"]: row["Reference"] for _, row in project_details_df.iterrows()}


def _programme_to_projects(project_details_df: pd.DataFrame) -> dict[str, list[str]]:
    """Creates a mapping from programme to a list of projects for that programme."""
    return {
        programme: project_details_df.loc[project_details_df["Local Authority"] == programme, "Full name"].tolist()
        for programme in project_details_df["Local Authority"].unique()
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


def _output_outcome_uoms(control_data_df: pd.DataFrame, column_name: str) -> dict[str, list[str]]:
    """Creates a mapping from standard/bespoke outcomes or ouputs to their unit of measurement.

    :param control_data_df: Dataframe of the extracted control data table
    :param column_name: String value of the column name from the relevant control table to be used for the mapping
    :return: Dictionary of output or outcome names to a list of their unit of measurement
    """
    return {
        row[column_name]: control_data_df.loc[control_data_df[column_name] == row[column_name], "UoM"].tolist()
        for _, row in control_data_df.iterrows()
        if not pd.isna(row["UoM"])
    }
