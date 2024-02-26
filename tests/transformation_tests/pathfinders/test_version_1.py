import pandas as pd

from core.transformation.pathfinders.version_1 import pathfinders_transform_v1


def test_pathfinders_transform_v1(
    mock_extracted_validated_data: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
    mock_project_name_to_id_mapping: dict[str, str],
    mock_programme_project_mapping: dict[str, list[str]],
):
    pathfinders_transform_v1(
        df_dict=mock_extracted_validated_data,
        reporting_round=1,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
        project_name_to_id_mapping=mock_project_name_to_id_mapping,
        programme_project_mapping=mock_programme_project_mapping,
    )
