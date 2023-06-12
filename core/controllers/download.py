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
from core.db.entities import Programme, Project, Submission, OutcomeData
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
    fund_ids = request.args.getlist("funds")
    organisation_ids = request.args.getlist("organisations")
    outcome_categories = request.args.getlist("outcome_categories")
    rp_start = request.args.get("rp_start")
    rp_end = request.args.get("rp_end")

    rp_start_datetime = datetime.strptime(rp_start, DATETIME_ISO_8610) if rp_start else None
    rp_end_datetime = datetime.strptime(rp_end, DATETIME_ISO_8610) if rp_end else None

    programmes, programme_outcomes, projects, project_outcomes = get_download_data(
        fund_ids, organisation_ids, outcome_categories, rp_start_datetime, rp_end_datetime
    )

    data = serialize_download_data(programmes, programme_outcomes, projects, project_outcomes)

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


def get_download_data(
    fund_ids: list[str],
    organisation_ids: list[str],
    outcome_categories: list[str],
    rp_start_datetime: datetime,
    rp_end_datetime: datetime,
) -> tuple[set[Programme], list[OutcomeData], set[Project], list[OutcomeData]]:
    """Runs a set of queries on the database to filter the returned download data by the filter query parameters.

    :param fund_ids: a list of fund_ids to filter on
    :param organisation_ids: a list of organisations_ids to filer on
    :param outcome_categories: a list of outcome categories to filter on
    :param rp_start_datetime: a reporting period start date to filter on
    :param rp_end_datetime: a reporting period end date to filter on
    :return:
    """
    # fund and organisation filter programme level data
    programmes = Programme.get_programmes_by_org_and_fund_type(
        organisation_ids=organisation_ids, fund_type_ids=fund_ids
    )

    # programmes filtered by outcome_category
    filtered_programmes, programme_outcomes = Programme.filter_programmes_by_outcome_category(
        programmes=programmes, outcome_categories=outcome_categories
    )
    programme_child_projects = [project for programme in filtered_programmes for project in programme.projects]

    # projects filtered by submissions and programmes
    submissions = Submission.get_submissions_by_reporting_period(start=rp_start_datetime, end=rp_end_datetime)
    projects = Project.get_projects_by_programme_ids_and_submission_ids(
        programme_ids=ids(programmes), submission_ids=ids(submissions)
    )

    # filter projects by outcome_category
    (
        filtered_projects,
        project_outcomes,
    ) = Project.filter_projects_by_outcome_categories(projects=projects, outcome_categories=outcome_categories)
    project_parent_programmes = Programme.query.filter(
        Programme.projects.any(Project.id.in_(ids(filtered_projects)))
    ).all()

    # combine projects and programmes into sets
    final_programmes = {*filtered_programmes, *project_parent_programmes}  # unique programmes
    final_projects = {*filtered_projects, *programme_child_projects}  # unique projects
    return final_programmes, programme_outcomes, final_projects, project_outcomes


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
