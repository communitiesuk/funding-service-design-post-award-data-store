import pandas as pd
import pytest
from resources.extracted_control_tables import EXTRACTED_CONTROL_TABLES
from resources.extracted_user_tables import EXTRACTED_USER_TABLES


@pytest.fixture(scope="module")
def mock_user_table_dict() -> dict[str, pd.DataFrame]:
    return EXTRACTED_USER_TABLES


@pytest.fixture(scope="module")
def mock_control_table_dict() -> dict[str, pd.DataFrame]:
    return EXTRACTED_CONTROL_TABLES


@pytest.fixture(scope="module")
def mock_programme_name_to_id_mapping() -> dict[str, str]:
    return {
        "Bolton Metropolitan Borough Council": "PF-BOL",
    }


@pytest.fixture(scope="module")
def mock_project_name_to_id_mapping() -> dict[str, str]:
    return {
        "Wellsprings Innovation Hub": "PF-BOL-001",
        "Bolton Market Upgrades": "PF-BOL-002",
        "Bolton Library & Museum Upgrade": "PF-BOL-003",
        "Public Realm Improvements": "PF-BOL-004",
        "Accelerated Funding £1 million Public Realm Improvements": "PF-BOL-005",
    }


@pytest.fixture(scope="module")
def mock_programme_project_mapping() -> dict[str, list[str]]:
    return {
        "PF-BOL": [
            "PF-BOL-001",
            "PF-BOL-002",
            "PF-BOL-003",
            "PF-BOL-004",
            "PF-BOL-005",
        ]
    }


@pytest.fixture(scope="module")
def mock_output_intervention_theme_mapping() -> dict[str, str]:
    return {"Total length of new pedestrian paths": "Enhancing sub-regional and regional connectivity"}


@pytest.fixture(scope="module")
def mock_outcome_intervention_theme_mapping() -> dict[str, str]:
    return {"Vehicle flow": "Unlocking and enabling industrial, commercial, and residential development"}
