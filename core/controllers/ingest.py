"""Provides a controller for spreadsheet ingestion."""
from io import BytesIO

import numpy as np
import pandas as pd
from flask import abort, current_app
from sqlalchemy import desc
from werkzeug.datastructures import FileStorage

from core.const import EXCEL_MIMETYPE, SUBMISSION_ID_FORMAT
from core.controllers.mappings import INGEST_MAPPINGS, DataMapping
from core.db import db
from core.db.entities import Submission
from core.errors import ValidationError
from core.extraction.towns_fund import ingest_towns_fund_data
from core.validation.casting import cast_to_schema
from core.validation.failures import InvalidEnumValueFailure
from core.validation.validate import validate

ETL_PIPELINES = {
    "tf_round_three": ingest_towns_fund_data,
}


def ingest(body, excel_file):
    """Ingests a spreadsheet submission and stores its contents in a database.

    This function takes in an Excel file object and extracts data from the file, casts it to the
    specified schema, and validates it.
    If source_type is specified, the data will be put through an etl pipeline, prior
    to validation.
    If the data fails validation, a `ValidationError` is raised. Otherwise, the data is cleaned and ingested into a
    database.

    :body: contains the request body params
    :excel_file: the Excel file to ingest, from the request body
    :return: A tuple containing a string message and an integer HTTP status code.
    :raises ValidationError: If the data fails validation against the specified schema.
    """
    source_type = body.get("source_type")  # required

    workbook = extract_data(excel_file=excel_file)

    if source_type:
        etl_pipeline = ETL_PIPELINES[source_type]
        workbook, _ = etl_pipeline(workbook)

    schema = current_app.config["VALIDATION_SCHEMA"]
    cast_to_schema(workbook, schema)
    validation_failures = validate(workbook, schema)

    # ignore enum validation and rely on db constraints for now
    validation_failures = [
        fail for fail in validation_failures if not isinstance(fail, InvalidEnumValueFailure)
    ]  # TODO: add nullable concept to validation and remove this

    if validation_failures:
        raise ValidationError(validation_failures=validation_failures)

    # TODO: this is not production ready - do we want to allow re-ingestion? if so, how?
    # this wipes the db in preparation to repopulate with the newly ingested spreadsheet
    db.drop_all()
    db.create_all()

    clean_data(workbook)
    populate_db(workbook, INGEST_MAPPINGS)

    submission_id = workbook["Submission_Ref"]["Submission ID"].iloc[0]
    save_submission_file(excel_file, submission_id)

    return "Success: Spreadsheet data ingested", 200


def extract_data(excel_file: FileStorage) -> dict[str, pd.DataFrame]:
    """Extract data from an excel_file.

    :param excel_file: an in-memory Excel file
    :return: DataFrames representing Excel sheets
    """
    if excel_file.content_type != EXCEL_MIMETYPE:
        return abort(400, "Invalid file type")

    try:
        workbook = pd.read_excel(
            BytesIO(excel_file.stream.read()).getvalue(),
            sheet_name=None,  # extract from all sheets
            engine="openpyxl",
        )
    except ValueError as ingest_err:
        if "Worksheet" in ingest_err.args[0]:
            return abort(400, "Invalid array of sheet names")
        return abort(500, "Internal Ingestion Error")

    return workbook


def clean_data(workbook: dict[str, pd.DataFrame]) -> None:
    """Clean the data in the given workbook by replacing all occurrences of `np.NA` with an empty string and `np.nan`
    with None.

    :param workbook: A dictionary where the keys are worksheet names and the values are Pandas dataframes representing
                     the contents of those worksheets.
    :return: None
    """
    for worksheet in workbook.values():
        worksheet.fillna("", inplace=True)  # broad replace of np.NA with empty string
        worksheet.replace({np.nan: None}, inplace=True)  # replaces np.NAT with None


def next_submission_id(reporting_round: int) -> str:
    """Get the next submission ID by incrementing the last in the DB.

    :return: The next submission ID.
    """
    latest_submission = (
        Submission.query.filter_by(reporting_round=reporting_round).order_by(desc(Submission.submission_id)).first()
    )
    if not latest_submission:
        return SUBMISSION_ID_FORMAT.format(reporting_round, 1)  # the first submission

    incremented_submission_num = latest_submission.submission_number + 1
    return SUBMISSION_ID_FORMAT.format(reporting_round, incremented_submission_num)


def populate_db(workbook: dict[str, pd.DataFrame], mappings: tuple[DataMapping]) -> None:
    """Populate the database with the data from the specified workbook using the provided data mappings.

    :param workbook: A dictionary containing data in the form of pandas dataframes.
    :param mappings: A tuple of DataMapping objects, which contain the necessary information for mapping the data from
                     the workbook to the database.
    :return: None
    """
    reporting_round = workbook["Submission_Ref"]["Reporting Round"].iloc[0]
    submission_id = next_submission_id(reporting_round)
    for mapping in mappings:
        worksheet = workbook[mapping.worksheet_name]
        if "Submission ID" in mapping.columns:
            worksheet["Submission ID"] = submission_id
        models = mapping.map_worksheet_to_models(worksheet)
        db.session.add_all(models)
    db.session.commit()


def save_submission_file(excel_file, submission_id):
    """Saves the submission Excel file.

    TODO: Store files in an S3 bucket, rather than the database.

    :param excel_file: The Excel file to save.
    :param submission_id: The ID of the submission to be updated.
    """
    submission = Submission.query.filter_by(submission_id=submission_id).first()
    submission.submission_filename = excel_file.filename
    excel_file.stream.seek(0)
    submission.submission_file = excel_file.stream.read()
    db.session.add(submission)
    db.session.commit()
