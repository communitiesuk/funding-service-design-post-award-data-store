import pytest


@pytest.fixture
def mocked_routes_trigger_async_download(mocker):
    return mocker.patch("find.main.routes.trigger_async_download", return_value=None)


@pytest.fixture
def mock_download_checkbox_data(mocker):
    mocker.patch(
        "find.main.routes.get_fund_checkboxes",
        return_value={
            "name": "funds",
            "items": [{"id": "FHSF", "name": "High Street Fund"}, {"id": "TFTD", "name": "Towns Fund - Town Deals"}],
        },
    )
    mocker.patch(
        "find.main.routes.get_region_checkboxes",
        return_value={
            "name": "regions",
            "items": [{"id": "TLC", "name": "North East"}, {"id": "TLI", "name": "London"}],
        },
    )
    mocker.patch(
        "find.main.routes.get_org_checkboxes",
        return_value={
            "name": "orgs",
            "items": [
                {"id": "747cdc34-48d3-11ef-a410-325096b39f47", "name": "Dudley Metropolitan Borough Council"},
                {"id": "7acebb84-48d3-11ef-ba35-325096b39f47", "name": "Dover District Council"},
            ],
        },
    )
    mocker.patch(
        "find.main.routes.get_outcome_checkboxes",
        return_value={
            "name": "outcomes",
            "items": ["Business", "Culture"],
        },
    )
    mocker.patch(
        "find.main.routes.get_returns",
        return_value={"end_date": "2023-02-01T00:00:00Z", "start_date": "2023-02-12T00:00:00Z"},
    )
