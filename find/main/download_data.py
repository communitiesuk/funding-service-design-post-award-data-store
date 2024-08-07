from datetime import datetime
from enum import StrEnum
from typing import Any

from data_store.controllers.get_filters import (
    get_funds,
    get_geospatial_regions,
    get_organisation_names,
    get_outcome_categories,
    get_reporting_period_range,
)


def financial_quarter_from_mapping(quarter: str, year: str) -> str | None:
    """
    Map the start date of a financial quarter based on user input.

    Args:
        quarter: The 'from' financial quarter selected by the user (must be 1, 2, 3, or 4)
        year: The 'from' financial year selected by the user

    Returns:
        Date string corresponding to the start of the chosen financial period in format 'YYYY-MM-DDTHH:MM:SSZ'),
        or None if the given quarter is invalid
    """
    start_year = year.split("/")[0]
    quarter_mapping = {
        "1": f"{start_year}-04-01T00:00:00Z",
        "2": f"{start_year}-07-01T00:00:00Z",
        "3": f"{start_year}-10-01T00:00:00Z",
        "4": f"{int(start_year) + 1}-01-01T00:00:00Z",
    }

    return quarter_mapping.get(quarter)


def financial_quarter_to_mapping(quarter: str, year: str) -> str | None:
    """
    Map the end date of a financial quarter based on user input.

    Args:
        quarter: The 'to' financial quarter selected by the user (must be 1, 2, 3, or 4)
        year: The 'to' financial year selected by the user

    Returns:
        Date string corresponding to the start of the chosen financial period in format 'YYYY-MM-DDTHH:MM:SSZ'),
        or None if the given quarter is invalid
    """
    end_year = year.split("/")[0]
    quarter_mapping = {
        "1": f"{end_year}-06-30T00:00:00Z",
        "2": f"{end_year}-09-30T00:00:00Z",
        "3": f"{end_year}-12-31T00:00:00Z",
        "4": f"{int(end_year) + 1}-03-31T00:00:00Z",
    }

    return quarter_mapping.get(quarter)


class FormNames(StrEnum):
    FUNDS = "funds"
    ORGS = "orgs"
    REGIONS = "regions"
    OUTCOMES = "outcomes"
    RETURNS_PERIOD = "funds"


def get_fund_checkboxes() -> dict[str, Any]:
    """Get checkbox data for the funds section.

    Calls API to get fund data and formats to checkbox data format.
    Example API data: [{"id": "FHSF", "name": "High Street Fund"}, {"id": "TFTD", "name": "Towns Fund - Town Deals"}]

    :return: checkbox data for funds
    """
    fund_data = get_funds()
    fund_checkboxes = {
        "name": FormNames.FUNDS,
        "items": fund_data,
    }
    return fund_checkboxes


def get_region_checkboxes() -> dict[str, Any]:
    """Get checkbox data for the regions section.

    Calls API to get region data and formats to checkbox data format.
    Example API data: [{"id": "TLC", "name": "North East"}, {"id": "TLI", "name": "London"}]

    :return: checkbox data for regions
    """
    region_data = get_geospatial_regions()
    region_checkboxes = {
        "name": FormNames.REGIONS,
        "items": region_data,
    }
    return region_checkboxes


def get_org_checkboxes() -> dict[str, Any]:
    """Get checkbox data for the orgs section.

    Calls API to get org data and formats to checkbox data format.
    Example API data: [
        {"id": "f5aa...64e", "name": "Dudley Metropolitan Borough Council"},
        {"id": "c6da...2dd", "name": "Dover District Council"},
    ]

    :return: checkbox data for orgs
    """
    org_data = get_organisation_names()
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
    outcome_data = get_outcome_categories()
    outcome_checkboxes = {
        "name": FormNames.OUTCOMES,
        "items": [{"id": outcome, "name": outcome} for outcome in outcome_data],
    }
    return outcome_checkboxes


def generate_financial_years(start_date, end_date):
    """Generate a list of financial years available based on the start and end dates provided by the db

    Args:
        start_date (datetime.date): The start date.
        end_date (datetime.date): The end date.

    Returns:
        list: A list of financial years in the format 'YYYY/YYYY+1', representing the range
            of dates. Each financial year is represented as a string.
    """

    # Adjust the years for the financial year
    min_year = start_date.year if start_date.month > 3 else start_date.year - 1
    max_year = end_date.year if end_date.month > 3 else end_date.year - 1

    # Generate the list of financial years
    financial_years = ["{}/{}".format(year, year + 1) for year in range(min_year, max_year + 1)]

    return financial_years


# TODO decide whether to implement this or leave all quarter options available
def generate_quarters(start_date, end_date):
    """Calculates which quarter the given min and max month resides in

    Returns:
        list: A list of quarters corresponding to the range of dates. Each quarter is
            represented by an integer (1, 2, 3, or 4).
    """

    start_quarter = (start_date.month - 1) // 3 + 1
    end_quarter = (end_date.month - 1) // 3 + 1

    quarter_options = [1, 2, 3, 4]

    return quarter_options[min(start_quarter, end_quarter) - 1 :: 1]


def get_returns() -> dict[str, Any]:
    """Retrieves data from /returns API endpoint and generates a dictionary of return period options.

    Returns:
        dict: A dictionary containing lists of return period options.
    """
    returns_data = get_reporting_period_range()

    if not returns_data:
        years = []
    else:
        start_date = datetime.date(returns_data["start_date"])
        end_date = datetime.date(returns_data["end_date"])
        years = generate_financial_years(start_date, end_date)

    returns_select = {
        "name": FormNames.RETURNS_PERIOD,
        "from-quarter": [1, 2, 3, 4],
        "to-quarter": [1, 2, 3, 4],
        "from-year": years,
        "to-year": years,
    }

    return returns_select
