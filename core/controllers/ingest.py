"""Provides a controller for spreadsheet ingestion."""
from io import BytesIO

import connexion
import numpy as np
import pandas as pd
from flask import abort, current_app
from werkzeug.datastructures import FileStorage

from core.const import EXCEL_MIMETYPE
from core.controllers.mappings import TOWNS_FUND_MAPPINGS, DataMapping
from core.db import db
from core.errors import ValidationError
from core.validation.casting import cast_to_schema
from core.validation.validate import validate


def ingest(body):
    """Ingests spreadsheet data and stores it in a database.

    This function takes in an Excel file object and a JSON schema name and extracts data from the file, casts it to the
    specified schema, and validates it. If the data fails validation, a `ValidationError` is raised. Otherwise, the
    data is cleaned and ingested into a database.

    Note: This implementation uses a `FakeDB` class that is not meant for production use and should be replaced
    with a proper database implementation.

    :param body: A dictionary containing the request body.
        - excel_file (required): A file object of an Excel spreadsheet to ingest.
        - schema (required): A string representing the name of the JSON schema to use for validation.
    :return: A tuple containing a string message and an integer HTTP status code.
    :raises ValidationError: If the data fails validation against the specified schema.
    """
    excel_file = connexion.request.files["excel_file"]  # required
    schema_name = body.get("schema")  # required, json schema enum

    workbook = extract_data(excel_file=excel_file)
    schema = current_app.config["SCHEMAS"][schema_name]
    cast_to_schema(workbook, schema)
    validation_failures = validate(workbook, schema)

    if validation_failures:
        raise ValidationError(validation_failures=validation_failures)

    # TODO: this is not production ready - do we want to allow re-ingestion? if so, how?
    # this wipes the db in preparation to repopulate with the newly ingested spreadsheet
    db.drop_all()
    db.create_all()

    clean_data(workbook)
    populate_db(workbook, TOWNS_FUND_MAPPINGS)

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


def populate_db(workbook: dict[str, pd.DataFrame], mappings: tuple[DataMapping]) -> None:
    """Populate the database with the data from the specified workbook using the provided data mappings.

    :param workbook: A dictionary containing data in the form of pandas dataframes.
    :param mappings: A tuple of DataMapping objects, which contain the necessary information for mapping the data from
                     the workbook to the database.
    :return: None
    """
    for mapping in mappings:
        worksheet = workbook[mapping.worksheet_name]
        models = mapping.map_worksheet_to_models(worksheet)
        db.session.add_all(models)
    db.session.commit()
