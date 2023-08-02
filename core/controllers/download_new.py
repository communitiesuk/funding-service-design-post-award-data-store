import json
from datetime import datetime

from flask import abort, make_response, request
from sqlalchemy import select

import core.db.entities as ents
from core.const import DATETIME_ISO_8610
from core.db import db
from core.db.queries import get_download_data_ids


def download():
    """Handle the download request and return the file in the specified format.

    Supported File Formats:
    - JSON: Returns the data as a JSON file.
    - XLSX: Returns the data as an Excel file with each table in a separate sheet.

    :return: Flask response object containing the file in the requested format.
    """
    file_format = request.args.get("file_format")
    fund_type_ids = request.args.getlist("funds")
    organisation_uuids = request.args.getlist("organisations")
    outcome_categories = request.args.getlist("outcome_categories")
    itl_regions = set(request.args.getlist("regions"))
    rp_start = request.args.get("rp_start")
    rp_end = request.args.get("rp_end")

    min_rp_start = datetime.strptime(rp_start, DATETIME_ISO_8610) if rp_start else None
    max_rp_end = datetime.strptime(rp_end, DATETIME_ISO_8610) if rp_end else None

    submission_uuids, programme_uuids, project_uuids = get_download_data_ids(
        min_rp_start, max_rp_end, organisation_uuids, fund_type_ids, itl_regions, outcome_categories
    )

    match file_format:
        case "json":
            json_data = serialize_json_data(submission_uuids, programme_uuids, project_uuids)
            file_content = json.dumps(json_data)
            content_type = "application/json"
            file_extension = "json"
        # case "xlsx":
        # xlsx_data = serialize_xlsx_data(programmes, programme_outcomes, projects, project_outcomes)
        # file_content = data_to_excel(xlsx_data)
        # content_type = EXCEL_MIMETYPE
        # file_extension = "xlsx"
        case _:
            return abort(400, f"Bad file_format: {file_format}.")

    response = make_response(file_content)
    response.headers.set("Content-Type", content_type)
    # Suffix the downloaded filename with current datetime in format yyyy-mm-dd-hhmmss
    current_datetime = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    response.headers.set("Content-Disposition", "attachment", filename=f"download-{current_datetime}.{file_extension}")

    return response


def serialize_json_data(submission_uuids, programme_uuids, project_uuids):
    # Place Details
    # TODO: do we test these queries? or just have end to end tests that assert on the final output?
    place_details_query = (
        select(
            ents.Submission.submission_id,
            ents.Programme.programme_id,
            ents.PlaceDetail.question,
            ents.PlaceDetail.answer,
            ents.PlaceDetail.indicator,
        )
        .join(ents.Submission, ents.Submission.id == ents.PlaceDetail.submission_id)
        .where(ents.Submission.id.in_(submission_uuids))
        .join(ents.Programme, ents.Programme.id == ents.PlaceDetail.programme_id)
        .where(ents.Programme.id.in_(programme_uuids))
    )

    place_details_rows = (tuple(row) for row in db.session.execute(place_details_query))
    place_details_serialized = [
        {
            "SubmissionID": sub_id,
            "ProgrammeID": prog_id,
            "Question": question,
            "Answer": answer,
            "Indicator": indicator,
        }
        for sub_id, prog_id, question, answer, indicator in place_details_rows
    ]

    # Project Details
    project_details_query = (
        select(
            ents.Submission.submission_id,
            ents.Programme.programme_id,
            ents.Project.project_id,
            ents.Project.project_name,
            ents.Project.primary_intervention_theme,
            ents.Project.location_multiplicity,
            ents.Project.locations,
            ents.Project.gis_provided,
            ents.Project.lat_long,
        )
        .where(ents.Project.id.in_(project_uuids))
        .join(ents.Submission, ents.Submission.id == ents.Project.submission_id)
        .where(ents.Submission.id.in_(submission_uuids))
        .join(ents.Programme, ents.Programme.id == ents.Project.programme_id)
        .where(ents.Programme.id.in_(programme_uuids))
    )

    project_details_rows = (tuple(row) for row in db.session.execute(project_details_query))
    project_details_serialized = [
        {
            "SubmissionID": sub_id,
            "ProgrammeID": prog_id,
            "ProjectID": proj_id,
            "ProjectName": proj_name,
            "PrimaryInterventionTheme": pit,
            "SingleorMultipleLocations": loc_multi,
            "Locations": loc,
            "AreYouProvidingAGISMapWithYourReturn": gis,
            "LatLongCoordinates": lat_long,
        }
        for sub_id, prog_id, proj_id, proj_name, pit, loc_multi, loc, gis, lat_long in project_details_rows
    ]

    return_json = {"Place Details": place_details_serialized, "Project Details": project_details_serialized}

    return return_json
