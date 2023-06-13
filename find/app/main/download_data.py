from enum import StrEnum
from typing import Any

from app.main.data import get_response
from config import Config


def quarter_to_date(quarter, year):
    # TODO: Implement this
    pass


class FormNames(StrEnum):
    FUNDS = "funds"
    ORGS = "orgs"
    AREAS = "areas"
    OUTCOMES = "outcomes"
    RETURNS_PERIOD = "funds"


def get_checkbox_data(endpoint):
    response = get_response(hostname=Config.DATA_STORE_API_HOST, endpoint=endpoint)

    # If the API returns 404, use empty array
    if response.status_code == 404:
        return []

    # Else, populate checkboxes with the response
    elif response.status_code == 200:
        return response.json()


def get_fund_checkboxes() -> dict[str, Any]:
    """Get checkbox data for the funds section.

    Calls API to get fund data and formats to checkbox data format.
    Example API data: [{"id": "FHSF", "name": "High Street Fund"}, {"id": "TFTD", "name": "Towns Fund - Town Deals"}]

    :return: checkbox data for funds
    """
    fund_data = get_checkbox_data("/funds")
    fund_checkboxes = {
        "name": FormNames.FUNDS,
        "items": fund_data,
    }
    return fund_checkboxes


def get_area_checkboxes() -> dict[str, Any]:
    """Get checkbox data for the areas section.

    This data is just hardcoded and covers all possible regions.

    :return: checkbox data for areas
    """
    area_data = [
        {"name": "North East", "id": "TLC"},
        {"name": "North West", "id": "TLD"},
        {"name": "Yorkshire and the Humber", "id": "TLE"},
        {"name": "East Midlands", "id": "TLF"},
        {"name": "West Midlands", "id": "TLG"},
        {"name": "East of England", "id": "TLH"},
        {"name": "London", "id": "TLI"},
        {"name": "South East", "id": "TLJ"},
        {"name": "South West", "id": "TLK"},
        {"name": "Scotland", "id": "TLM"},
        {"name": "Wales", "id": "TLL"},
        {"name": "Northern Ireland", "id": "TLN"},
    ]
    area_checkboxes = {
        "name": FormNames.AREAS,
        "items": area_data,
    }
    return area_checkboxes


def get_org_checkboxes() -> dict[str, Any]:
    """Get checkbox data for the orgs section.

    Calls API to get org data and formats to checkbox data format.
    Example API data: [
        {"id": "f5aa...64e", "name": "Dudley Metropolitan Borough Council"},
        {"id": "c6da...2dd", "name": "Dover District Council"},
    ]

    :return: checkbox data for orgs
    """
    org_data = get_checkbox_data("/organisations")
    org_checkboxes = {
        "name": FormNames.ORGS,
        "items": org_data,
    }
    return org_checkboxes


def get_outcome_checkboxes() -> dict[str, Any]:
    """Get checkbox data for the outcomes section.

    Calls API to get outcome data and formats to checkbox data format.
    Example API data: ["Business", "Culture"]

    :return: checkbox data for outcomes
    """
    outcome_data = get_checkbox_data("/outcome-categories")
    outcome_checkboxes = {
        "name": FormNames.OUTCOMES,
        # display Other instead of Custom
        "items": [
            {"id": outcome, "name": outcome if outcome != "Custom" else "Other"}
            for outcome in outcome_data
        ],
    }
    return outcome_checkboxes


returns = {
    "name": FormNames.RETURNS_PERIOD,
    "quarter": (1, 2, 3, 4),
    "year": ("2022/2023", "2023/2024"),
}
