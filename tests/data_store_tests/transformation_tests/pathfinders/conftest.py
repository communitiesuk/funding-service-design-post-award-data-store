import pytest


@pytest.fixture(scope="module")
def mock_programme_name_to_id_mapping() -> dict[str, str]:
    return {
        "Bolton Council": "PF-BOL",
    }


@pytest.fixture(scope="module")
def mock_project_name_to_id_mapping() -> dict[str, str]:
    return {
        "PF-BOL-001: Wellsprings Innovation Hub": "PF-BOL-001",
        "PF-BOL-002: Bolton Market Upgrades": "PF-BOL-002",
        "PF-BOL-003: Bolton Library & Museum Upgrade": "PF-BOL-003",
        "PF-BOL-004: Public Realm Improvements": "PF-BOL-004",
        "PF-BOL-005: Accelerated Funding £1 million Public Realm Improvements": "PF-BOL-005",
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
