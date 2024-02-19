import pandas as pd

from core.transformation.pathfinders.version_1 import pathfinders_transform_v1


def test_pathfinders_transform_v1(
    mock_extracted_validated_data: dict[str, pd.DataFrame],
    mock_programme_project_mapping: dict[str, list[dict[str, str]]],
):
    pathfinders_transform_v1(mock_extracted_validated_data, mock_programme_project_mapping)
