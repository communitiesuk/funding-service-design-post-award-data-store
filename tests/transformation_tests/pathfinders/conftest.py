import pandas as pd
import pytest
from resources.extracted_validated_data import (
    extracted_validated_dict,
    programme_project_mapping,
)


@pytest.fixture(scope="module")
def mock_extracted_validated_data() -> dict[str, pd.DataFrame]:
    return extracted_validated_dict


@pytest.fixture(scope="module")
def mock_programme_project_mapping() -> dict[str, list[dict[str, str]]]:
    return programme_project_mapping
