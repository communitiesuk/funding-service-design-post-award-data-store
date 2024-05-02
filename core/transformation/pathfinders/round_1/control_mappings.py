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
    """
    project_details_df = extracted_tables["Project details control"]
    return {
        "programme_name_to_id": _programme_name_to_id(project_details_df),
        "project_name_to_id": _project_name_to_id(project_details_df),
    }


def _programme_name_to_id(project_details_df: pd.DataFrame) -> dict[str, str]:
    """Creates a mapping from programme name to programme ID."""
    return {row["Local Authority"]: row["Reference"][:6] for _, row in project_details_df.iterrows()}


def _project_name_to_id(project_details_df: pd.DataFrame) -> dict[str, str]:
    """Creates a mapping from project name to project ID."""
    return {row["Full name"]: row["Reference"] for _, row in project_details_df.iterrows()}
