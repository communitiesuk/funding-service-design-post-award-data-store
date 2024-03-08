import pandas as pd


def create_control_mappings(extracted_tables: dict[str, pd.DataFrame]) -> dict[str, dict | list[str]]:
    """
    Creates mappings from control data tables to be used for validation and transformation downstream. Mappings created
    are:
        - Programme name    -> Programme ID
        - Project name      -> Project ID
        - Programme ID      -> List of Project IDs
        - Programme ID      -> List of allowed bespoke outputs
        - Programme ID      -> List of allowed bespoke outcomes
    """
    project_details_df = extracted_tables["Project details control"]
    bespoke_outputs_df = extracted_tables["Bespoke outputs control"]
    bespoke_outcomes_df = extracted_tables["Bespoke outcomes control"]
    return {
        "programme_name_to_id": _programme_name_to_id(project_details_df),
        "project_name_to_id": _project_name_to_id(project_details_df),
        "programme_id_to_project_ids": _programme_id_to_project_ids(project_details_df),
        "programme_id_to_allowed_bespoke_outputs": _programme_id_to_allowed_bespoke_outputs(
            bespoke_outputs_df, _programme_name_to_id(project_details_df)
        ),
        "programme_id_to_allowed_bespoke_outcomes": _programme_id_to_allowed_bespoke_outcomes(
            bespoke_outcomes_df, _programme_name_to_id(project_details_df)
        ),
    }


def _programme_name_to_id(project_details_df: pd.DataFrame) -> dict[str, str]:
    return {row["Local Authority"]: row["Reference"][:6] for _, row in project_details_df.iterrows()}


def _project_name_to_id(project_details_df: pd.DataFrame) -> dict[str, str]:
    return {row["Project name"]: row["Reference"] for _, row in project_details_df.iterrows()}


def _programme_id_to_project_ids(project_details_df: pd.DataFrame) -> dict[str, list[str]]:
    return {
        programme_id: project_details_df.loc[
            project_details_df["Reference"].str.startswith(programme_id), "Reference"
        ].tolist()
        for programme_id in _programme_name_to_id(project_details_df).values()
    }


def _programme_id_to_allowed_bespoke_outputs(
    bespoke_outputs_df: pd.DataFrame, programme_name_to_id: dict[str, str]
) -> dict[str, list[str]]:
    return {
        programme_id: bespoke_outputs_df.loc[bespoke_outputs_df["Local Authority"] == programme_name, "Output"].tolist()
        for programme_name, programme_id in programme_name_to_id.items()
    }


def _programme_id_to_allowed_bespoke_outcomes(
    bespoke_outcomes_df: pd.DataFrame, programme_name_to_id: dict[str, str]
) -> dict[str, list[str]]:
    return {
        programme_id: bespoke_outcomes_df.loc[
            bespoke_outcomes_df["Local Authority"] == programme_name, "Outcome"
        ].tolist()
        for programme_name, programme_id in programme_name_to_id.items()
    }
