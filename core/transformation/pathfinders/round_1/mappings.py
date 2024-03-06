import pandas as pd


def create_mappings(extracted_tables: dict[str, list[pd.DataFrame]]) -> dict[str, dict | list[str]]:
    project_mapping_df = extracted_tables["Project details"]
    standard_outputs_df = extracted_tables["Standard outputs"]
    standard_outcomes_df = extracted_tables["Standard outcomes"]
    bespoke_outputs_df = extracted_tables["Bespoke outputs"]
    bespoke_outcomes_df = extracted_tables["Bespoke outcomes"]
    return {
        "programme_name_to_id": _programme_name_to_id(project_mapping_df),
        "project_name_to_id": _project_name_to_id(project_mapping_df),
        "programme_id_to_project_ids": _programme_id_to_project_ids(project_mapping_df),
        "allowed_standard_outputs": _allowed_standard_outputs(standard_outputs_df),
        "allowed_standard_outcomes": _allowed_standard_outcomes(standard_outcomes_df),
        "programme_id_to_allowed_bespoke_outputs": _programme_id_to_allowed_bespoke_outputs(
            bespoke_outputs_df, _programme_name_to_id(project_mapping_df)
        ),
        "programme_id_to_allowed_bespoke_outcomes": _programme_id_to_allowed_bespoke_outcomes(
            bespoke_outcomes_df, _programme_name_to_id(project_mapping_df)
        ),
    }


def _programme_name_to_id(project_mapping_df: pd.DataFrame) -> dict[str, str]:
    return {row["Local Authority"]: row["Reference"][:6] for _, row in project_mapping_df.iterrows()}


def _project_name_to_id(project_mapping_df: pd.DataFrame) -> dict[str, str]:
    return {row["Project Name"]: row["Reference"] for _, row in project_mapping_df.iterrows()}


def _programme_id_to_project_ids(project_mapping_df: pd.DataFrame) -> dict[str, list[str]]:
    return {
        programme_id: project_mapping_df.loc[
            project_mapping_df["Reference"].str.startswith(programme_id), "Reference"
        ].tolist()
        for programme_id in _programme_name_to_id(project_mapping_df).values()
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


def _allowed_standard_outputs(standard_outputs_df: pd.DataFrame) -> list[str]:
    return [row["Standard outputs"] for _, row in standard_outputs_df.iterrows()]


def _allowed_standard_outcomes(standard_outcomes_df: pd.DataFrame) -> list[str]:
    return [row["Standard outcomes"] for _, row in standard_outcomes_df.iterrows()]
