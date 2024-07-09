import io
import json
from collections import namedtuple
from datetime import datetime
from enum import StrEnum
from typing import Any
from urllib.parse import urlencode

import requests
from flask import abort, current_app

from app.const import MIMETYPE
from app.main.data import get_response
from config import Config


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


def get_region_checkboxes() -> dict[str, Any]:
    """Get checkbox data for the regions section.

    Calls API to get region data and formats to checkbox data format.
    Example API data: [{"id": "TLC", "name": "North East"}, {"id": "TLI", "name": "London"}]

    :return: checkbox data for regions
    """
    region_data = get_checkbox_data("/regions")
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
    returns_data = get_checkbox_data("/reporting-period-range")

    if not returns_data:
        years = []
    else:
        start_date = datetime.strptime(returns_data["start_date"].split("T")[0], "%Y-%m-%d")
        end_date = datetime.strptime(returns_data["end_date"].split("T")[0], "%Y-%m-%d")
        years = generate_financial_years(start_date, end_date)

    returns_select = {
        "name": FormNames.RETURNS_PERIOD,
        "from-quarter": [1, 2, 3, 4],
        "to-quarter": [1, 2, 3, 4],
        "from-year": years,
        "to-year": years,
    }

    return returns_select


def process_api_response(query_params: dict) -> tuple:
    """Processes the API response for a file download request.

    :param query_params: Query parameters for the API request.

    :return: A tuple containing:
            - The content type of the API response (str).
            - Either the BytesIO object containing the file content (for valid responses),
              or a tuple representing an error response (status code, error message).

    Raises:
        abort(500): If an unexpected content type is received from the API.
    """
    response = get_response(Config.DATA_STORE_API_HOST, "/download", query_params=query_params)

    content_type = response.headers["content-type"]

    if content_type == MIMETYPE.JSON:
        file_content = io.BytesIO(json.dumps(response.json()).encode("UTF-8"))
    elif content_type == MIMETYPE.XLSX:
        file_content = io.BytesIO(response.content)
    else:
        current_app.logger.error(
            "Response with unexpected content type received from API: {content_type}",
            extra=dict(content_type=content_type),
        )
        return abort(500), f"Unknown content type: {content_type}"

    return content_type, file_content


def process_async_download(query_params: dict):
    """process async download request to start the background process.
    :param query_params: (dict): Query parameters for the API request.
    """
    request_url = (
        Config.DATA_STORE_API_HOST
        + "/trigger_async_download"
        + ("?" + urlencode(query_params, doseq=True) if query_params else "")
    )
    requests.post(request_url, timeout=20)


def get_presigned_url(filename: str):
    """Get the presigned link for the short time to retrieve the file from s3 bucket.
    :param filename (str): object name which needs to be retrieved from s3 if exists
    Raises:ValueError: If object doest not exists in S3, it will raise an error.
    Returns:Returns the response the API.
    """
    if not filename:
        raise ValueError("filename is required")

    response = get_response(Config.DATA_STORE_API_HOST, f"/get-presigned-url/{filename}")
    return response.json()["presigned_url"]


FileMetadata = namedtuple("FileMetadata", ["response_status_code", "formated_date", "file_format", "file_size_str"])


def get_find_download_file_metadata(filename: str) -> FileMetadata:
    """To get the object metadata from S3 using the ovject Key
    :param filename (str): object name to get the metadata

    Raises:
        ValueError: If object doest not exists in S3, it will raise an error.

    Returns: FileMetadata:
             - Returns the last modified date,
             -file format, and human-readable file size.
    """
    response = get_response(Config.DATA_STORE_API_HOST, f"/get-find-download-metadata/{filename}")
    response_status_code = response.status_code

    if response_status_code == 200:
        metadata = response.json()
        file_size = metadata["content_length"]
        file_size_str = get_human_readable_file_size(file_size)
        last_modified_date = metadata["last_modified"]
        content_type = metadata["content_type"]

        date = datetime.fromisoformat(last_modified_date)
        formated_date = date.strftime("%d %B %Y")

        if content_type == MIMETYPE.XLSX:
            file_format = "Microsoft Excel spreadsheet"
        elif content_type == MIMETYPE.JSON:
            file_format = "JSON"
        else:
            file_format = "Unknown type"

        return FileMetadata(response_status_code, formated_date, file_format, file_size_str)
    else:
        return FileMetadata(response_status_code, None, None, None)


def get_human_readable_file_size(file_size_bytes: int) -> str:
    """Return a human-readable file size string.
    :param file_size_bytes: file size in bytes,
    :return: human-readable file size,
    """

    file_size_kb = round(file_size_bytes / 1024, 1)
    if file_size_kb < 1024:
        return f"{round(file_size_kb, 1)} KB"
    elif file_size_kb < 1024 * 1024:
        return f"{round(file_size_kb / 1024, 1)} MB"
    else:
        return f"{round(file_size_kb / (1024 * 1024), 1)} GB"
