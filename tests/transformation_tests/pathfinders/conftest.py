import pandas as pd
import pytest
from resources.extracted_mapping_tables import EXTRACTED_MAPPING_TABLES
from resources.extracted_user_data_tables import EXTRACTED_USER_DATA_TABLES

from tables.table import Cell, Table


@pytest.fixture(scope="module")
def mock_user_data_table_dict() -> dict[str, pd.DataFrame]:
    return EXTRACTED_USER_DATA_TABLES


@pytest.fixture(scope="module")
def mock_tables_dict() -> dict[str, Table]:
    return {
        table_name: Table(
            df=df,
            id_tag="EXAMPLE-ID-TAG",
            worksheet=table_name,
            start_tag=Cell(0, 0),
            col_idx_map={col: idx for idx, col in enumerate(df.columns)},
        )
        for table_name, df in EXTRACTED_USER_DATA_TABLES.items()
    }


@pytest.fixture(scope="module")
def mock_mapping_table_dict() -> dict[str, pd.DataFrame]:
    return EXTRACTED_MAPPING_TABLES


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


@pytest.fixture(scope="module")
def mock_programme_id_to_allowed_bespoke_outputs() -> dict[str, list[str]]:
    return {"PF-BOL": ["Amount of new office space (m2)"]}


@pytest.fixture(scope="module")
def mock_programme_id_to_allowed_bespoke_outcomes() -> dict[str, list[str]]:
    return {"PF-BOL": ["Travel times in corridors of interest"]}


@pytest.fixture()
def mock_mappings(
    mock_programme_name_to_id_mapping,
    mock_project_name_to_id_mapping,
    mock_programme_project_mapping,
    mock_output_intervention_theme_mapping,
    mock_outcome_intervention_theme_mapping,
    mock_programme_id_to_allowed_bespoke_outputs,
    mock_programme_id_to_allowed_bespoke_outcomes,
) -> dict[str, dict[str, str] | dict[str, list[str]]]:
    return {
        "programme_name_to_id": mock_programme_name_to_id_mapping,
        "project_name_to_id": mock_project_name_to_id_mapping,
        "programme_id_to_project_ids": mock_programme_project_mapping,
        "allowed_standard_outputs": mock_output_intervention_theme_mapping,
        "allowed_standard_outcomes": mock_outcome_intervention_theme_mapping,
        "programme_id_to_allowed_bespoke_outputs": mock_programme_id_to_allowed_bespoke_outputs,
        "programme_id_to_allowed_bespoke_outcomes": mock_programme_id_to_allowed_bespoke_outcomes,
    }
