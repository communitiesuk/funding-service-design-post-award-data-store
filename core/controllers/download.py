"""
This module provides a Flask endpoint for downloading data from a database. The endpoint supports two file formats: JSON
and Excel. It retrieves data from the database and returns the data in the requested format.
"""
import io
import json
from datetime import datetime

import pandas as pd
from flask import abort, make_response, request

from core.const import DATETIME_ISO_8610, EXCEL_MIMETYPE

# isort: off
from core.db.entities import Organisation, Programme, Project, Submission, OutcomeData
from core.serialization.download_json_serializer import serialize_download_data
from core.util import ids


# isort: on


def download():
    """Handle the download request and return the file in the specified format.

    Supported File Formats:
    - JSON: Returns the data as a JSON file.
    - XLSX: Returns the data as an Excel file with each table in a separate sheet.

    :return: Flask response object containing the file in the requested format.
    """
    file_format = request.args.get("file_format")
    funds = request.args.getlist("fund")
    organisations = request.args.getlist("organisation")
    outcome_categories = request.args.getlist("outcome_categories")
    rp_start = request.args.get("rp_start")
    rp_end = request.args.get("rp_end")

    rp_start_datetime = datetime.strptime(rp_start, DATETIME_ISO_8610) if rp_start else None
    rp_end_datetime = datetime.strptime(rp_end, DATETIME_ISO_8610) if rp_end else None

    # fund and organisation filter programme level data
    organisations = Organisation.get_organisations_by_name(organisations)
    programmes = Programme.get_programmes_by_org_and_fund_type(organisation_ids=ids(organisations), fund_type_ids=funds)

    # reporting periods filter submissions, which along with programme filter project level data
    submissions = Submission.get_submissions_by_reporting_period(start=rp_start_datetime, end=rp_end_datetime)
    projects = Project.get_project_by_programme_ids_and_submission_ids(
        programme_ids=ids(programmes), submission_ids=ids(submissions)
    )

    # outcome categories filter outcome data from filtered projects
    outcomes = OutcomeData.get_outcomes_by_project_ids_and_categories(
        project_ids=ids(projects), categories=outcome_categories
    )

    data = serialize_download_data(organisations, programmes, projects, outcomes)
    match file_format:
        case "json":
            file_content = json.dumps(data)
            content_type = "application/json"
            file_extension = "json"
        case "xlsx":
            file_content = data_to_excel(data)
            content_type = EXCEL_MIMETYPE
            file_extension = "xlsx"
        case _:
            return abort(400, f"Bad file_format: {file_format}.")

    response = make_response(file_content)
    response.headers.set("Content-Type", content_type)
    response.headers.set("Content-Disposition", "attachment", filename=f"download.{file_extension}")

    return response


def data_to_excel(data: dict[str, list[dict]]) -> bytes:
    """Convert a dictionary of lists of dictionaries to an Excel file and return the file content as bytes.

    This function takes a dictionary mapping sheet names to sheet data and converts them into separate sheets in an
    Excel file. The sheet name corresponds to the key in the dictionary, and the list of row data is written to each
    sheet. The resulting Excel file content is returned as bytes.

    :param data: A dictionary where keys represent sheet names and values are lists of dictionaries, each representing
                 a row in the data.
    :return: The content of the Excel file as bytes.
    """
    buffer = io.BytesIO()
    writer = pd.ExcelWriter(buffer, engine="xlsxwriter")
    for sheet_name, sheet_data in data.items():
        df = pd.DataFrame(data=sheet_data)
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    writer.save()
    buffer.seek(0)
    file_content = buffer.getvalue()
    return file_content
